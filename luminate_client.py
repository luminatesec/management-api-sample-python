import configparser
import logging
import datetime
from luminate_python import Luminate

logger = logging.getLogger(__name__)
CONF_FP = 'conf/luminate.properties'
APPS_FP = 'conf/luminate.applications'
LUMINATE_ENVIRONMENT = 'Luminate Properties'
API_VERSION = 1


# Setting up the environment based on the information provided through the configuration file conf/luminate.properties
def setup_env():

    # Parsing Luminate environment configuration file
    logger.debug("Parsing Luminate environment configuration file: %s" % CONF_FP)

    luminate_dic = configparser.ConfigParser()
    try:
        dataset = luminate_dic.read(CONF_FP)
    except Exception as e:
        logger.critical("Failed reading Luminate environment configuration file: %s - %s"% (CONF_FP, e))
        return None

    if len(dataset) == 0:
        logger.critical("Failed reading Luminate environment configuration file: %s "% CONF_FP)
        return None

    try:
        tenant_name = luminate_dic.get(LUMINATE_ENVIRONMENT,'tenant_name')
        luminate_domain = luminate_dic.get(LUMINATE_ENVIRONMENT,'luminate_domain')
        client_id = luminate_dic.get(LUMINATE_ENVIRONMENT,'client_id')
        client_secret = luminate_dic.get(LUMINATE_ENVIRONMENT,'client_secret')
    except Exception as e:
        logger.critical("Failed parsing Luminate environment configuration file: %s - %s"% (CONF_FP, e))
        return None

    # Creating a Luminate Security Object (Oauth based authentication)
    logger.debug("Creating Luminate Object (Oauth based authentication) - tenant name: %s, Luminate domain: %s" % (tenant_name, luminate_domain))
    base_url='https://api.{}.{}'.format(tenant_name, luminate_domain)

    try:
        luminate = Luminate(base_url, API_VERSION, client_id, client_secret)
    except Exception as e:
        logger.critical(e)
        return None
    return luminate


# Assigns configured user/group to the provided application
def assign_user_to_app(luminate, app, app_id):

    if not 'email' in app:
        logger.debug("No user was configured for assignments")
        return 0

    logger.debug("Assigning user: %s to application: %s" % (app['email'], app_id))

    if 'idp' in app:
        idp = app['idp']
    else:
        idp = ""

    try:
        luminate.assign_entity_to_app(app_id, app['email'], idp)

    except Exception as e:
        logger.critical("Failed to assign user %s to an application %s: %s" % (app['email'], app_id, str(e)))
        return -1


# Creates a Luminate Security application and assigns a user to it in case one was configured
def config_app(luminate, app):

    if 'app_name' in app and 'app_type' in app and 'internal_address' in app and 'site_name' in app:
        app_name = app['app_name']
        app_type = app['app_type']
        internal_address = app['internal_address']
        site_name = app['site_name']
    else:
        logger.critical("Failed Parsing applications configuration file: %s, missing properties" % (APPS_FP))
        return -1

    if 'description' in app:
        description = app['description']
    else:
        description = ""

    # Creating a Luminate Security application based on the information provided at conf/luminate.applications
    logger.debug("Creating an application %s based on the information provided at %s" %(app_name, APPS_FP))

    try:
        app_id = luminate.create_application(app_name, description, app_type, internal_address, site_name)
    except Exception as e:
        logger.critical(e)
        return -1

    return assign_user_to_app(luminate, app, app_id)


# Parsing Application configuration file
def configure_apps(luminate):

    logger.debug("Reading applications configuration file:%s" %APPS_FP)
    apps_dic = configparser.ConfigParser()
    try:
        dataset = apps_dic.read(APPS_FP)
    except Exception as e:
        logger.critical("Failed reading applications configuration file: %s - %s"% (APPS_FP, e))
        return -1

    if len(dataset) == 0:
        logger.critical("Failed reading applications configuration file: %s " % APPS_FP)
        return -1
    for each_section in apps_dic.sections():
        app = dict(apps_dic.items(each_section))
        logger.debug("Parsing Luminate applications configuration file %s, section: %s " % (APPS_FP, app))
        config_app(luminate, app)
    return 0


def execute():

    logfile = 'logs/' + datetime.datetime.now().strftime('luminate_client_%Y_%m_%d_%H_%M_%S.log')
    logging.basicConfig(filename=logfile, level=logging.DEBUG)

    luminate = setup_env()
    if luminate is None:
        return -1

    return configure_apps(luminate)


if __name__ == '__main__':
    execute()



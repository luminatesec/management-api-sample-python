import configparser
import logging
import datetime
from luminate_python import Luminate
import sys

logger = logging.getLogger('luminate_client')
CONF_FP = 'conf/luminate.properties'
APPS_FP = 'conf/luminate.applications'
LUMINATE_ENVIRONMENT = 'Luminate Properties'
API_VERSION = 1


# Setting up the environment based on the information provided through the configuration file conf/luminate.properties
def setup_env(conf_file):
    # Parsing Luminate environment configuration file
    logger.debug("Parsing Luminate environment configuration file: %s" % conf_file)

    luminate_dic = configparser.ConfigParser()
    try:
        dataset = luminate_dic.read(conf_file)
    except Exception as e:
        logger.critical("Failed reading Luminate environment configuration file: %s - %s" % (conf_file, e))
        return None

    if len(dataset) == 0:
        logger.critical("Failed reading Luminate environment configuration file: %s " % conf_file)
        return None

    try:
        tenant_name = luminate_dic.get(LUMINATE_ENVIRONMENT, 'tenant_name')
        luminate_domain = luminate_dic.get(LUMINATE_ENVIRONMENT, 'luminate_domain')
        client_id = luminate_dic.get(LUMINATE_ENVIRONMENT, 'client_id')
        client_secret = luminate_dic.get(LUMINATE_ENVIRONMENT, 'client_secret')
    except Exception as e:
        logger.critical("Failed parsing Luminate environment configuration file: %s - %s" % (conf_file, e))
        return None

    # Creating a Luminate Security Object (Oauth based authentication)
    logger.debug("Creating Luminate Object (Oauth based authentication) - tenant name: %s, Luminate domain: %s" %
                 (tenant_name, luminate_domain))
    base_url = 'https://api.{}.{}'.format(tenant_name, luminate_domain)

    verify_ssl = True
    if luminate_dic.has_option(LUMINATE_ENVIRONMENT, 'verify_ssl'):
        verify_ssl = luminate_dic.getboolean(LUMINATE_ENVIRONMENT, 'verify_ssl')

    try:
        luminate = Luminate(base_url, API_VERSION, client_id, client_secret, verify_ssl)
    except Exception as e:
        logger.critical(e)
        return None
    return luminate


# Assigns configured user/group to the provided application
def assign_entity_to_app(luminate, app, app_id):
    if 'email' in app:
        assign_user_to_app(luminate, app, app_id)
    elif 'group_name' in app:
        assign_group_to_app(luminate, app, app_id)
    else:
        logger.debug("No assignments were defined for application id: %s" % app_id)
        return 0


def assign_user_to_app(luminate, app, app_id):
    logger.debug("Assigning user: %s to application: %s" % (app['email'], app_id))

    if 'idp' in app:
        idp = app['idp']
    else:
        logger.critical("No Identity Provider was configured for user: %s" % app['email'])
        return -1

    assigned_ssh_users = app.get('assigned_ssh_users', None)
    if assigned_ssh_users:
        assigned_ssh_users = app['assigned_ssh_users'].split(',')

    try:
        luminate.assign_user_to_app(app_id, app['email'], idp, assigned_ssh_users)

    except Exception as e:
        logger.critical("Failed to assign user %s to an application %s: %s" % (app['email'], app_id, str(e)))
        return -1


def assign_group_to_app(luminate, app, app_id):
    logger.debug("Assigning group: %s to application: %s" % (app['group_name'], app_id))

    if 'idp' in app:
        idp = app['idp']
    else:
        logger.critical("No Identity Provider was configured for group: %s" % app['group_name'])
        return -1

    assigned_ssh_users = app.get('assigned_ssh_users', None)
    if assigned_ssh_users:
        assigned_ssh_users = app['assigned_ssh_users'].split(',')

    try:
        luminate.assign_group_to_app(app_id, app['group_name'], idp, assigned_ssh_users)

    except Exception as e:
        logger.critical("Failed to assign group %s to an application %s: %s" % (app['group_name'], app_id, str(e)))
        return -1


# Creates a Luminate Security application and assigns a user to it in case one was configured
def config_app(luminate, app):
    if 'app_name' in app and 'app_type' in app and 'internal_address' in app and 'site_name' in app:
        app_name = app['app_name']
        app_type = app['app_type']
        internal_address = app['internal_address']
        site_name = app['site_name']
        ssh_users = app.get('ssh_users', None)
        if ssh_users:
            ssh_users = app['ssh_users'].split(',')
    else:
        logger.critical("Failed Parsing applications configuration file: %s, missing properties" % APPS_FP)
        return -1

    if 'description' in app:
        description = app['description']
    else:
        description = ""

    # Creating a Luminate Security application based on the information provided at conf/luminate.applications
    logger.debug("Creating an application %s based on the information provided at %s" % (app_name, APPS_FP))

    try:
        app_id = luminate.create_app(app_name, description, app_type, internal_address, site_name, ssh_users)
    except Exception as e:
        logger.critical(e)
        return -1
    description += " Automatically generated by Luminate API client"
    try:
        luminate.update_app(app_id, app_name, description, app_type, internal_address, site_name, ssh_users)
    except Exception as e:
        logger.critical(e)

    return assign_entity_to_app(luminate, app, app_id)


# Parsing Application configuration file
def configure_apps(luminate, apps_conf_file):
    logger.debug("Reading applications configuration file:%s" % apps_conf_file)
    apps_dic = configparser.ConfigParser()
    try:
        dataset = apps_dic.read(apps_conf_file)
    except Exception as e:
        logger.critical("Failed reading applications configuration file: %s - %s" % (apps_conf_file, e))
        return -1

    if len(dataset) == 0:
        logger.critical("Failed reading applications configuration file: %s " % apps_conf_file)
        return -1
    for each_section in apps_dic.sections():
        app = dict(apps_dic.items(each_section))
        logger.debug("Parsing Luminate applications configuration file %s, section: %s " % (apps_conf_file, app))
        config_app(luminate, app)
    return 0


def execute():
    logfile = 'logs/' + datetime.datetime.now().strftime('luminate_client_%Y_%m_%d_%H_%M_%S.log')
    logging.basicConfig(filename=logfile, level=logging.DEBUG)

    # log to stdout as well
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s] - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    luminate = setup_env(CONF_FP)
    if luminate is None:
        return -1

    return configure_apps(luminate, APPS_FP)


if __name__ == '__main__':
    execute()

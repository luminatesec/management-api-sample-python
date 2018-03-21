#!/usr/bin/python

"""
This module implements a friendly interface between the raw JSON
responses from Luminate and the Resource/dict abstractions provided by this library. Users
will construct a Luminate object as described below.
"""

import json
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import logging


class Luminate(object):
    """User interface to Luminate.
    Clients interact with Luminate by constructing an instance of this object and calling its methods.
    """

    def __init__(self, server, rest_api_version, client_id, client_secret, verify_ssl=True):
        """Construct a JIRA client instance.
        :param server -- the server address and context path to use. Defaults to ``http://localhost:2990/jira``.
        :param rest_api_version -- the version of the REST resources under rest_path to use. Defaults to ``1``.
        :param client_id -- client_id as provided by the OAuth Provider (Luminate Security)
        :param client_secret -- client_secret as provided by the OAuth Provider (Luminate Security)
        """
        self._options = {'server': server, 'rest_api_version': rest_api_version}

        self._create_oauth_session(client_id, client_secret, verify_ssl)
        self._logger = logging.getLogger(__name__)

    def _create_oauth_session(self, client_id, client_secret, verify_ssl=True):

        token_url = '{}/v1/oauth/token'.format(self._options['server'])

        client = BackendApplicationClient(client_id=client_id)
        client.prepare_request_body()
        oauth = OAuth2Session(client=client)
        token = oauth.fetch_token(token_url=token_url,
                                  client_id=client_id,
                                  client_secret=client_secret,
                                  verify=verify_ssl)

        self._session = oauth

        return token

    def create_app(self, app_name, description, app_type, internal_address, site_name, ssh_users):
        """Create a new Application at a specific Site.
        :param app_name: Application Name
        :param description: A string which describes the application
        :param app_type: Application type - Valid values are HTTP, SSH.
        :param internal_address: Application internal IP
        :param site_name: The name of the site on which this application resides.
        :param ssh_users: A list of user names that are available for SSH log-in on the remote ssh machine.

        """
        connection_settings = {'internal_address': internal_address}

        url_template = '{}/v{}/applications'
        url = url_template.format(self._options['server'], self._options['rest_api_version'])

        payload = {
            'name': app_name,
            'description': description,
            'type': app_type,
            'connection_settings': connection_settings,
            'site_name': site_name,
        }

        if app_type == 'SSH':
            if ssh_users:
                payload['ssh_users'] = ssh_users
            else:
                raise ValueError('A request for creating an SSH application must include SSH users')

        response = self._session.post(url, data=json.dumps(payload))
        self._logger.debug("Request to Luminate for creating an application :%s returned response: %s, status code:%s"
                           % (app_name, response.content, response.status_code))

        if response.status_code != 201:
            response.raise_for_status()
            return None

        data = response.json()

        return data['id']

    def update_app(self, app_id, app_name, description, app_type, internal_address, site_name, ssh_users):
        """Updates an existing application.
        :param app_id: Application ID
        :param app_name: Application Name
        :param description: A string which describes the application
        :param app_type: Application type - Valid values are HTTP, SSH.
        :param internal_address: Application internal IP
        :param site_name: The name of the site on which this application resides.
        :param ssh_users: A list of user names that are available for SSH log-in on the remote ssh machine.

         """

        connection_settings = {'internal_address': internal_address}

        url_template = '{}/v{}/applications/{}'

        url = url_template.format(self._options['server'], self._options['rest_api_version'], app_id)
        payload = {
            'name': app_name,
            'description': description,
            'type': app_type,
            'connection_settings': connection_settings,
            'site_name': site_name,
        }

        if app_type == 'SSH':
            if ssh_users:
                payload['ssh_users'] = ssh_users
            else:
                raise ValueError(
                    'Request to Luminate for updating an application %s failed - missing SSH users' % app_name)

        response = self._session.put(url, data=json.dumps(payload))
        self._logger.debug("Request to Luminate for updating an application :%s returned response: %s, status code:%s"
                           % (app_name, response.content, response.status_code))

        if response.status_code != 200:
            response.raise_for_status()
            return -1

        return 0

    def assign_user_to_app(self, app_id, email, idp, ssh_users):
        """
        Assign a user to an application.
        :param app_id: Application ID
        :param email: The e-mail address of the user to whom you would like to grant access to the application.
        :param idp: Identity Provider of the user.
        :param ssh_users: A list of user names with which the user will be able to log-in to the ssh machine.

        """

        url_template = '{}/v{}/applications/{}/assign-user'

        url = url_template.format(self._options['server'], self._options['rest_api_version'], app_id)
        payload = {
            'email': email,
            'idp_name': idp
        }

        if ssh_users:
            payload['ssh_users'] = ssh_users
            self._logger.debug("SSH users: %s were defined for user: %s" % (ssh_users, email))

        response = self._session.post(url, data=json.dumps(payload))

        self._logger.debug("Request to Luminate for assigning a user :%s to application %s returned response:\n %s,\
                            status code:%s" % (email, app_id, response.content, response.status_code))

        if response.status_code != 200:
            response.raise_for_status()
            return -1

        return 0

    def assign_group_to_app(self, app, name, idp, ssh_users):
        """
        Assign a group to an application.
        :param app: Application ID
        :param name: The name of the group to which you would like to grant access to the application.
        :param idp: Identity Provider of the group.
        :param ssh_users: A list of user names with which the group members will be able to log-in to the ssh machine.

        """

        url_template = '{}/v{}/applications/{}/assign-group'

        url = url_template.format(self._options['server'], self._options['rest_api_version'], app)
        payload = {
            'name': name,
            'idp_name': idp
        }

        if ssh_users:
            payload['ssh_users'] = ssh_users
            self._logger.debug("SSH users: %s were defined for group: %s" % (ssh_users, name))

        response = self._session.post(url, data=json.dumps(payload))

        self._logger.debug("Request to Luminate for assigning a group :%s to application %s returned response:\n %s,\
                            status code:%s" % (name, app, response.content, response.status_code))

        if response.status_code != 200:
            response.raise_for_status()
        return 0

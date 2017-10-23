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

    def __init__(self, server, rest_api_version,client_id, client_secret):
        """Construct a JIRA client instance.
        :param server -- the server address and context path to use. Defaults to ``http://localhost:2990/jira``.
        :param rest_api_version -- the version of the REST resources under rest_path to use. Defaults to ``1``.
        :param client_id -- client_id as provided by the OAuth Provider (Luminate Security)
        :param client_secret -- client_secret as provided by the OAuth Provider (Luminate Security)
        """
        self._options = {}
        self._options['server'] = server
        self._options['rest_api_version'] = rest_api_version

        self._create_oauth_session(client_id, client_secret)
        self._logger = logging.getLogger(__name__)

    def _create_oauth_session(self, client_id, client_secret):

        token_url = '{}/v1/oauth/token'.format(self._options['server'])

        client = BackendApplicationClient(client_id=client_id)
        client.prepare_request_body()
        oauth = OAuth2Session(client=client)
        token = oauth.fetch_token(token_url=token_url,
                                  client_id=client_id,
                                  client_secret=client_secret)

        self._session = oauth

        return token

    def create_application(self, app_name, description, app_type, internal_address, site_name):
        """Create a new Application at a specific Site.
        :param app_name: Application Name
        :param description: A string which describes the application
        :param type: Application type - Valid values are HTTP, SSH.
        :param internal_address: Application internal IP
        :param site_name: The name of the site on which this application resides.
        :param email: The e-mail address of the user to whom you would like to grant access to the application.
        :param idp: Identity Provider of the user. This field should be empty in case of a local user.

        """
        connection_settings = {'internal_address': internal_address}

        url_template = '{}/v{}/applications'
        url = url_template.format(self._options['server'], self._options['rest_api_version'])

        payload = {
            'name': app_name,
            'description': description,
            'type':app_type,
            'connection_settings': connection_settings,
            'site_name': site_name,
        }

        response = self._session.post(url, data=json.dumps(payload))
        self._logger.debug("Request to Luminate for creating an application :%s returned response: %s, status code:%s" \
                           % (app_name, response.content,response.status_code))

        if response.status_code != 201:
            raise ValueError(
                'Request to Luminate for creating an application %s returned an error %s, the response is:\n%s'
                % (app_name, response.status_code, response.text)

            )
            return None

        data = response.json()

        return data['id']

    def assign_entity_to_app(self, app, email, idp):
        """
        Assign a user/group to an application.
        :param app: Application ID
        :param email: The e-mail address of the user to whom you would like to grant access to the application.
        :param idp: Identity Provider of the user. This field should be empty in case of a local user.

        """

        url_template = '{}/v{}/applications/{}/assign-user'

        url = url_template.format(self._options['server'], self._options['rest_api_version'], app)
        payload = {
            'email': email,
            'idp_name': idp
        }

        response = self._session.post(url, data=json.dumps(payload))

        self._logger.debug("Request to Luminate for assigning a user :%s to application %s returned response:\n %s,\
                            status code:%s" % (email,app,response.content,response.status_code))

        if response.status_code != 200:
            raise ValueError(
                'Request to Luminate for for assigning a user :%s to application %s returned an error %s,'
                'response is:\n%s'
                % (email, app, response.status_code, response.text)
            )
        return True

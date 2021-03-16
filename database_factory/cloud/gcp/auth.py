#!/usr/bin/env python3

"""
File handles the authentication to Google Cloud Platform account and return
the specified Google Cloud Platform Service client.
"""

import os
import logging
import traceback
from enum import Enum

import google.auth
from google.oauth2.service_account import Credentials
from google.cloud import resource_manager
from google.cloud import secretmanager


logger = logging.getLogger(__name__)


class ConnectionType(Enum):
    """
    Enum class to declare the type of Google Cloud Platform Services.

    ********
    Attributes:
    --------

        RESOUCEMANAGER:     Google Cloud Platform Resource Manager Service.
        SECRETMANAGER:      Google Cloud Platform Secret Manager Service.
    """

    RESOUCEMANAGER = 1
    SECRETMANAGER = 2


class GcpAuthManager(object):
    """
    Class handle the authentication on Google Cloud Platform account and return
    the client of requested Google Cloud Platform Service.

    ********
    Methods:
    --------

        __init__:                       Initaization class object.
        __get_credentials__:            Return the credentails of Google Cloud
                                        Platform account.
        get_project_name:               Method return the project name of
                                        Google Cloud Platform.
        get_resource_manager_client:    Return the client of GCP Resource
                                        Manager Service
        get_secret_manager_client:      Return the client of GCP Secret Manager
                                        Service
        get_client:                     Return the client of requested GCP Service
    """

    def __init__(self, service_accout_file=None):
        """
        Initialization function to Google Cloud Platform authentication class.

        ***********
        Attributes:
        -----------

            service_accout_file:    (Optional) => Google Cloud Platform service
                                    account file for authentication. If not
                                    provided will use authentication from
                                    server metadata or from environment
                                    "GOOGLE_APPLICATION_CREDENTIALS". 
                                    Default: None to get credentails from
                                    server.
        """

        self.service_accout_file = service_accout_file

    def __get_credentials__(self):
        """
        Method to authenticate to Google CLoud Platform account and return
        credentails and project id.

        *******
        Return:
        -------

            credentials:    Credentials of Google Cloud Platform account.
            project_id:     Project ID of Google Cloud Platform project.
        """

        scopes = ["https://www.googleapis.com/auth/cloud-platform"]
        service_file = self.service_accout_file
        if service_file and os.path.exists(service_file):
            credentials = Credentials.from_service_account_file(service_file,
                                                                scopes=scopes)
            project_id = credentials.project_id
        else:
            credentials, project_id = google.auth.default(scopes=scopes)

        return credentials, project_id

    def get_project_name(self):
        """
        Method to return the project id of Google Cloud Platform account.

        *******
        Return:
        -------

            project_id:     Project ID of Google Cloud Platform project.
        """

        _, project_id = self.__get_credentials__()
        return project_id

    def get_resource_manager_client(self):
        """
        Method to return client of GCP Resource Manager Service

        *******
        Return:
        -------

            client:     Client of GCP Resource Manager Service.
        """

        credentials, _ = self.__get_credentials__()
        client = resource_manager.Client(credentials=credentials)
        return client

    def get_secret_manager_client(self):
        """
        Method to return client of GCP Secret Manager Service

        *******
        Return:
        -------

            client:     Client of GCP Secret Manager Service.
        """

        credentials, _ = self.__get_credentials__()
        client = secretmanager.SecretManagerServiceClient(
            credentials=credentials)
        return client

    @staticmethod
    def get_client(conn_type, service_accout_file=None):
        """
        Method to return the client of requested Google Cloud Platform Service.

        ***********
        Return:
        -----------

            client:     Client of requested Google Cloud Platform Service.
        """

        try:
            logger.info("Get the client of requested GCP Service")
            if isinstance(conn_type, ConnectionType):
                cm = GcpAuthManager(service_accout_file=service_accout_file)

                if conn_type is ConnectionType.RESOUCEMANAGER:
                    logger.info(
                        "Get the client of GCP Resource Manager Service")
                    return cm.get_resource_manager_client()
                elif conn_type is ConnectionType.SECRETMANAGER:
                    logger.info("Get the client of GCP Secret Manager Service")
                    return cm.get_secret_manager_client()
                else:
                    raise ValueError('Invalid connection type requested')
            else:
                raise ValueError(
                    'conn_type is not type of ConnectionType Enum')
        except Exception as err:
            logger.exception("Failed to get the client of GCP Service")
            traceback.print_tb(err.__traceback__)
            raise

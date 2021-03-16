#!/usr/bin/env python3

"""
File used to handle the Google Cloud Platform Secret Manager Service.
"""

import logging
import traceback
import json
from google.cloud import secretmanager

from .auth import ConnectionType
from .auth import GcpAuthManager
from .resource_manager import ResourceManager


logger = logging.getLogger(__name__)


class SecreteManager(object):
    """
    Class handle the operations on Google Cloud Platform Secret Manager Service

    ********
    Methods:
    --------

        __init__:           Initaization class object.
        __get_client__:     Method to get client of GCP Secret Manager Service.
        get_secrete:        Fetch secrets of Secret Name from Google Cloud
                            Platform Secret Manager Service.
    """

    def __init__(self, service_account_file=None):
        """
        Initialization function to initlaize Secret Manager

        ***********
        Attributes:
        -----------

            service_account_file:   (Optional) => Google Cloud Platform service
                                    account file for authentication. If not
                                    provided will use authentication from
                                    server metadata or from environment
                                    "GOOGLE_APPLICATION_CREDENTIALS". 
                                    Default: None to get credentails from
                                    server.
        """

        self.service_account_file = service_account_file

    def __get_client__(self):
        """
        Method to return the client of GCP Secret Manager Service

        *******
        Retrun:
        -------

            client:     Client of GCP Secret Manager Service
        """

        client = GcpAuthManager.get_client(
            ConnectionType.SECRETMANAGER, service_accout_file=self.service_account_file)
        return client

    @staticmethod
    def get_secrete(secrete_id, service_account_file=None):
        """
        Method to fetch the secrets from GCP Secret Manager Service of provided
        secret name.

        ***********
        Attributes:
        -----------

            secrete_id:             (Required) => Name of secret whose secrets
                                    need to fetch from Google Cloud Platform
                                    Secret Manager Service.
            service_account_file:   (Optional) => Google Cloud Platform service
                                    account file for authentication. If not
                                    provided will use authentication from
                                    server metadata or from environment
                                    "GOOGLE_APPLICATION_CREDENTIALS". 
                                    Default: None to get credentails from
                                    server.
        *******
        Retrun:
        -------

            payload:        Secrets of secret name from GCP Secret Manager
                            Service.
        """

        try:
            logger.info("Fetch secrets from GCP Secret Manager Service")
            sec_mgr = SecreteManager(service_account_file=service_account_file)
            client = sec_mgr.__get_client__()

            project_number = ResourceManager.get_project_number(
                service_account_file=service_account_file)
            parent = f"projects/{project_number}/secrets/{secrete_id}/versions/latest"

            response = client.access_secret_version(request={"name": parent})

            payload = response.payload.data.decode("UTF-8")

            return payload
        except Exception as err:
            logger.error(
                "Failed to fetch secrets from GCP Secret Manager Service")
            logger.exception(err)
            traceback.print_tb(err.__traceback__)
            raise

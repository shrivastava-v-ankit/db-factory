#!/usr/bin/env python3

"""
File used to handle the Google Cloud Platform Resource Manager Service.
"""

import logging
import traceback
import json
from google.cloud import resource_manager

from .auth import ConnectionType
from .auth import GcpAuthManager


logger = logging.getLogger(__name__)


class ResourceManager(object):
    """
    Class handle the operations on Google Cloud Platform Resource Manager
    Service.

    ********
    Methods:
    --------

        __init__:               Initaization class object.
        __get_client__:         Method to get client of Google Cloud Platform
                                Resource Manager Service.
        get_project_metadata:   Fetch secrets of Secret Name from Google Cloud
                                Platform Secret Manager Service.
        get_project_number:     Fetch the unique Project number of GCP account.
    """

    def __init__(self, service_account_file=None):
        """
        Initialization function to initlaize Resource Manager

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
        Method to return the client of GCP Resource Manager Service

        *******
        Retrun:
        -------

            client:     Client of GCP Resource Manager Service
        """

        client = GcpAuthManager.get_client(
            ConnectionType.RESOUCEMANAGER, service_accout_file=self.service_account_file)
        return client

    @staticmethod
    def get_project_metadata(service_account_file=None):
        """
        Method to return the project metadata of Google Cloud Platform account.

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
        *******
        Retrun:
        -------

            project_metadata:       Project metadata of Google Cloud Platform
                                    account.
        """

        try:
            logger.info(
                "Fetch project metadata from GCP Resource Manager Service")
            res_mgr = ResourceManager(
                service_account_file=service_account_file)
            client = res_mgr.__get_client__()

            gcp_auth = GcpAuthManager(service_accout_file=service_account_file)
            project_id = gcp_auth.get_project_name()

            project_metadata = client.fetch_project(project_id=project_id)

            logger.info(
                "Successfully fetched project metadata from GCP Resource Manager Service")

            return project_metadata
        except Exception as err:
            logger.error(
                "Failed to fetch project metadata from GCP Resource Manager Service")
            logger.exception(err)
            traceback.print_tb(err.__traceback__)
            raise

    @staticmethod
    def get_project_number(service_account_file=None):
        """
        Method to return the unique Project number of Google Cloud Platform
        account.

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
        *******
        Retrun:
        -------

            project_number:         Unique Project number of Google Cloud
                                    Platform account.
        """

        try:
            logger.info(
                "Fetch unique project number from GCP Resource Manager Service")
            project_metadata = ResourceManager.get_project_metadata(
                service_account_file=service_account_file)

            project_number = project_metadata.number

            logger.info(
                "Successfully fetched unique project number from GCP Resource Manager Service")

            return project_number
        except Exception as err:
            logger.error(
                "Failed to fetch project number from GCP Resource Manager Service")
            logger.exception(err)
            traceback.print_tb(err.__traceback__)
            raise

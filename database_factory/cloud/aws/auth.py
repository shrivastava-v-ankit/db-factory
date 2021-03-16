#!/usr/bin/env python3

"""
File handles the authentication to AWS account and return the specified
AWS Service client.
"""

import os
import logging
import traceback
from enum import Enum
import boto3

logger = logging.getLogger(__name__)


class ConnectionType(Enum):
    """
    Enum class to declare the type of AWS Services.

    ********
    Attributes:
    --------

        SECRETMANAGER:      AWS Secret Manager Service.
    """

    SECRETMANAGER = 1


class AwsAuthManager(object):
    """
    Class handle the authentication on AWS account and return the client of
    requested AWS Service.

    ********
    Methods:
    --------

        __init__:                   Initaization class object.
        __get_session__:            Return the session of AWS connection.
        get_secret_manager_client:  Method to get client of AWS Secret Manager
                                    Service.
        get_client:                 Return the client of requested AWS Service
    """

    def __init__(self, region: str = 'us-east-1'):
        """
        Initialization function to initlaize Secret Manager

        ***********
        Attributes:
        -----------

            region:     (Optional) => AWS region holds Secret Manager Service.
                        Default: AWS Region 'us-east-1'
        """

        self.region = 'us-east-1'
        if region:
            self.region = region

    def __get_session__(self):
        """
        Method to return the session of AWS connection.

        ***********
        Return:
        -----------

            session:     Session of AWS connection.
        """
        session = boto3.session.Session()
        return session

    def get_secret_manager_client(self):
        """
        Method to return client of AWS Secret Manager Service

        ***********
        Return:
        -----------

            client:     Client of AWS Secret Manager Service.
        """

        session = self.__get_session__()
        client = session.client(
            service_name='secretsmanager',
            region_name=self.region
        )
        return client

    @staticmethod
    def get_client(conn_type: ConnectionType, region: str = 'us-east-1'):
        """
        Method to return the client of requested AWS Service.

        ***********
        Return:
        -----------

            client:     Client of requested AWS Service.
        """

        try:
            logger.info("Get the client of requested AWS Service")
            if isinstance(conn_type, ConnectionType):
                cm = AwsAuthManager(region=region)

                if conn_type is ConnectionType.SECRETMANAGER:
                    logger.info("Get the client of AWS Secret Manager Service")
                    return cm.get_secret_manager_client()
                else:
                    raise ValueError('Invalid connection type requested')
            else:
                raise ValueError(
                    'conn_type is not type of ConnectionType Enum')
        except Exception as err:
            logger.exception("Failed to get the client of AWS Service")
            traceback.print_tb(err.__traceback__)
            raise

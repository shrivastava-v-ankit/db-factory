#!/usr/bin/env python3

"""
File used to handle the AWS Secret Manager Serice.
"""

import logging
import traceback
import json
import base64
from botocore.exceptions import ClientError

from .auth import ConnectionType
from .auth import AwsAuthManager

logger = logging.getLogger(__name__)
logging.getLogger('boto3').setLevel(logging.INFO)
logging.getLogger('botocore').setLevel(logging.INFO)

ERROR_CODES = {
    "DecryptionFailureException": "Secrets Manager can't decrypt the protected secret text using the provided KMS key.",
    "InternalServiceErrorException": "An error occurred on the server side.",
    "InvalidParameterException": "You provided an invalid value for a parameter.",
    "InvalidRequestException": "You provided a parameter value that is not valid for the current state of the resource.",
    "ResourceNotFoundException": "We can't find the resource that asked."}


class SecreteManager(object):
    """
    Class handle the operations on AWS Secret Manager Service.

    ********
    Methods:
    --------

        __init__:           Initaization class object.
        __get_client__:     Method to get client of AWS Secret Manager Service.
        get_secrete:        Fetch secrets of Secret Name from AWS Secret
                            Manager Service.
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

        logger.info(
            f"Secret Manager is initalized for AWS region: {self.region}")

    def __get_client__(self):
        """
        Method to return the client of AWS Secret Manager Service

        *******
        Retrun:
        -------

            client:     Client of AWS Secret Manager Service
        """
        client = AwsAuthManager.get_client(ConnectionType.SECRETMANAGER,
                                           region=self.region)
        return client

    @staticmethod
    def get_secrete(secret_name: str, region: str = 'us-east-1'):
        """
        Method to fetch the secrets from AWS Secret Manager Service of provided
        secret name.

        ***********
        Attributes:
        -----------

            secret_name:    (Required) => Name of secret whose secrets need to
                            fetch from AWS Secret Manager Service.
            region:         (Optional) => AWS region holds Secret Manager
                            Service.
                            Default: AWS Region 'us-east-1'

        *******
        Retrun:
        -------

            payload:        Secrets of secret name from AWS Secret Manager
                            Service.
        """

        try:
            logger.info("Fetch secrets from AWS Secret Manager Service")
            sec_mgr = SecreteManager(region=region)
            client = sec_mgr.__get_client__()

            response = client.get_secret_value(SecretId=secret_name)
        except ClientError as e:
            logger.error(
                "Failed to fetch secrets from AWS Secret Manager Service")

            if e.response['Error']['Code'] in ERROR_CODES:
                logger.exception(ERROR_CODES[e.response['Error']['Code']])
                raise e
        else:
            # Decrypts secret using the associated KMS CMK.
            # Depending on whether the secret is a string or binary, one of these fields will be populated.
            if 'SecretString' in response:
                payload = response['SecretString']
            else:
                payload = base64.b64decode(response['SecretBinary'])

        return payload

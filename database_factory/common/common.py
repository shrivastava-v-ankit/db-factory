#!/usr/bin/env python

"""
File to common methods exposed as static under Common class.
"""

import logging

logger = logging.getLogger(__name__)


class Common(object):
    """
    Class handle the common utility methods.

    ********
    Methods:
    --------

        get_secret:                 Method to get the secrets from AWS or GCP
                                    cloud hosting the Secret manager service.
        normaize_connection_dict:   Method to convert the key of dictonary
                                    in upper case to ensure uniform access.
    """

    @staticmethod
    def get_secret(secret_id: str,
                   secrete_manager_cloud: str,
                   aws_region: str = "us-east-1"):
        """
        Method helps to fetch the secrets from cloud secret manager service.
        This helps us to not expose the password and other secrets as plain
        text.

        ***********
        Attributes:
        -----------

            secret_id:              (Required) => Secret Id containing json
                                    for connection parameters under secret
                                    manager services of AWS or GCP.
                                    AWS / GCP credentials should be set as
                                    default and will be fetched from server
                                    metadata.
            secrete_manager_cloud:  (Required) => Cloud exposing Secret
                                    manager service. Supported cloud are
                                    * aws
                                    * gcp
            aws_region:             (Optional) => AWS region where Secret
                                    manager service is hosted.
                                    Default: us-east-1
                                    This parameter is considered onluy when
                                    secrete_manager_cloud is set as aws.
        *******
        Return:
        -------

            connection_dict:        Dictonary of secret ensuring key of
                                    dictonary is set to upper case for uniform
                                    access.
        """
        logger.info(f'Fetching secrets from cloud secret manager')
        param = None

        if secrete_manager_cloud in ["gcp"]:
            logger.info(f'Using GCP as cloud secret manager')
            from ..cloud.gcp.secrete_manager import SecreteManager
        elif secrete_manager_cloud in ["aws"]:
            logger.info(f'Using AWS as cloud secret manager')
            from ..cloud.aws.secrete_manager import SecreteManager
            param = aws_region
        else:
            logger.error(
                f'unsupported cloud "{secrete_manager_cloud}" for secret manager service')
            raise ValueError("Unsupported cloud for secrete manager")

        payload = SecreteManager.get_secrete(secret_id, param)
        connection_dict = eval(payload)
        return connection_dict

    @staticmethod
    def normaize_connection_dict(connection_dict: dict,
                                 is_to_upper: bool = False):
        """
        Method helps to normalize the key name of dictonary to upper case.
        This helps even mixed case keys are provided will help further
        execution to handle the keys as reuired by application.

        ***********
        Attributes:
        -----------

            connection_dict:    (Required) => Dictonary object to normalize the
                                keys.
            is_to_upper:        (Optional) => If True keys will be normalized
                                to upper case else to lower case.
                                Default: False
        *******
        Return:
        -------

            conn_dict:          Dictonary to set keys to upper case for uniform
                                access.
        """
        if is_to_upper:
            conn_dict = {key.upper(): value for key,
                         value in connection_dict.items()}
        else:
            conn_dict = {key.lower(): value for key,
                         value in connection_dict.items()}
        return conn_dict

#!/usr/bin/env python

"""
File holds the module of Migration database manager and decide to connect with
multiple databases using the configuration parameters.
URI of database handled automatically for multiple databases using SQLAlchemy
"""

import os
import sys
import logging
import traceback
from urllib.parse import quote_plus as urlquote
from pandas import DataFrame
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData

from .common.common import Common
from .operations import Operations

logger = logging.getLogger(__name__)

SUPPORTED_ENGINE = ["postgres", "mysql", "mariadb",
                    "snowflake", "bigquery", "sqlite"]
SUPPORTED_SECRET_MANAGER_CLOUD = ["aws", "gcp"]


class DatabaseManager(object):
    """
    Class handle the Database Manager using SQLAlchemy Dialects for different databases.

    ********
    Methods:
    --------

        __init__:               Initaization functions
        fetch_from_secret:      Method to fetch the values from Cloud Secret
                                Manager Service.
        create_uri:             Method uses the initalization parameter and
                                create the uri for the provided engine with
                                proper driver.
        create_session:         Method to create the SQLAlchemy session for the
                                initalized the engine type.
        execute_sql:            Function to execute DML or DDL queries and return
                                with rows if rows exist.
        execute_df:             Function to execute Pandas DataFrame object.
        get_df:                 Function to execute DML select queries and return
                                as Pandas DataFrame.
        object
    """

    def __init__(self,
                 engine_type: str,
                 database: str,
                 sqlite_db_path: str = None,
                 username: str = None,
                 password: str = None,
                 schema: str = "public",
                 host: str = None,
                 port: str = None,
                 snowflake_role: str = None,
                 snowflake_warehouse: str = None,
                 snowflake_account: str = None,
                 secret_id: str = None,
                 secrete_manager_cloud: str = "aws",
                 aws_region: str = "us-east-1",
                 detail_logs: bool = False
                 ):
        """
        Initialization function to initlaize the object

        ***********
        Attributes:
        -----------

            engine_type:            (Required) => Type of Engine of database.
                                    One of the below supported engines:
                                    * postgres
                                    * mysql
                                    * mariadb
                                    * snowflake
                                    * bigquery
                                    * sqlite
            database:               (Required) => Database name to connect.
                                    Database must be precreated.
            sqlite_db_path:         (Optional) => Fully qualifiled path where
                                    database will be created. Database file be
                                    named as per database paramater.
                                    Default: Current user home directory
            username:               (Optional) => Username to connect database.
                                    User should have all permissions on
                                    database. This value can be set in secret
                                    manager rather as plain text.
            password:               Optional) => Password as plain text to
                                    connect database. This value can be set in
                                    secret manager rather as plain text.
            schema:                 (Optional) => Name of Schema of database.
                                    Valid for Snowflake and Postgres.
                                    Default: is 'public'
            host:                   (Optional) => Hostname of IP address of RDS
                                    server.  This value can be set in secret
                                    manager rather as plain text.
            port:                   (Optional) => Port of RDS server. This
                                    value can be set in secret manager rather
                                     as plain text.
            snowflake_role:         (Optional) => Snowflake role for connection.
                                    This value can be set in secret manager
                                    rather as plain text.
            snowflake_warehouse:    (Optional) => Snowflake wharehouse for
                                    connection. This value can be set in secret
                                    manager rather as plain text.
            snowflake_account:      (Optional) => Snowflake account for
                                    connection. This value can be set in secret
                                    manager rather as plain text.
            secret_id:              (Optional) => Prefered way to set the json
                                    object of connection parameters in secret
                                    manager services of AWS or GCP.
                                    If running on AWS / GCP servers then server
                                    should have permissions to read the secrets
                                    from secret manager service.
                                    AWS / GCP credentials should be set as
                                    default and will be fetched from server
                                    metadata.
            secrete_manager_cloud:  (Optional) => Prefered way to get secrets.
                                    Default: is 'aws'
                                    One of supported secret manager service
                                    cloud provider:
                                    * aws
                                    * gcp
            aws_region:             (Optional) => AWS region for secret manager
                                    service.
                                    Default: is 'us-east-1'
            detail_logs:            (Optional) => Detailed logs for debugging.
                                    Default: Fasle.
        """
        self.engine_type = engine_type
        self.database = database

        if not sqlite_db_path:
            # Check current OS, it is Windows or Linux
            is_windows = sys.platform.lower().startswith('win')
            if is_windows:
                sqlite_db_path = (
                    f"{os.environ['HOMEDRIVE']}"
                    f"{os.environ['HOMEPATH']}"
                )
            else:
                sqlite_db_path = os.environ['HOME']

        self.sqlite_db_path = sqlite_db_path
        self.username = username
        self.password = password
        self.schema = schema
        self.host = host
        self.port = port
        self.snowflake_role = snowflake_role
        self.snowflake_account = snowflake_account
        self.snowflake_warehouse = snowflake_warehouse
        self.secret_id = secret_id
        self.secrete_manager_cloud = secrete_manager_cloud
        self.aws_region = aws_region
        self.engine = None
        self.session = None
        self.detail_logs = detail_logs

    def fetch_from_secret(self):
        """
        Method to fetch the values from Cloud Secret Manager Service.
        Use the class variables for the paramaters.

        *******
        Return:
        -------

            secret: Secrets if secret id is provided else None
        """
        secret = None

        if self.secret_id and self.secrete_manager_cloud:
            logger.info(f'Fetch secrets from cloud secret manager service')
            try:
                secret = Common.get_secret(
                    secret_id=self.secret_id,
                    secrete_manager_cloud=self.secrete_manager_cloud,
                    aws_region=self.aws_region)
            except Exception as err:
                logger.exception(
                    f'Failed to fetch secrets from the Secret Manager Service', err)
        else:
            logger.info(
                f'Secret id is not set. Will use plain authentication.')

        return secret

    def create_uri(self):
        """
        Method uses the initalization parameter and create the uri for the
        the provided engine with proper driver.
        Use the class variables for the paramaters.

        *******
        Return:
        -------

            uri:                    URI required for creating SQLAlchemy
                                    connection.     
            param:                  Extra kwargs for SQLAlchemy connection.
            is_not_dialect_desc:    True if want to remove the support of
                                    SQLAlchemy Dialects description.
        """

        logger.info(f"Create URI for the engine '{self.engine}'")

        if self.engine_type not in SUPPORTED_ENGINE:
            msg = (
                f"Unsupported engine '{self.engine_type}'."
                f" Supported are '{SUPPORTED_ENGINE}'"
            )
            logger.error(msg)
            raise ValueError(msg)

        # Fetch the secret first to initalize the values.
        secret = self.fetch_from_secret()

        if secret:
            # Normalize the secret to upper key to ensure corectness of dictonary
            secret = Common.normaize_connection_dict(connection_dict=secret,
                                                     is_to_upper=True)
            if "USERNAME" in secret:
                self.username = secret["USERNAME"]
            if "PASSWORD" in secret:
                self.password = secret["PASSWORD"]
            if "SCHEMA" in secret:
                self.schema = secret["SCHEMA"]
            if "HOST" in secret:
                self.host = secret["HOST"]
            if "PORT" in secret:
                self.port = secret["PORT"]
            if "SNOWFLAKE_ROLE" in secret:
                self.snowflake_role = secret["SNOWFLAKE_ROLE"]
            if "SNOWFLAKE_ACCOUNT" in secret:
                self.snowflake_account = secret["SNOWFLAKE_ACCOUNT"]
            if "SNOWFLAKE_WAREHOUSE" in secret:
                self.snowflake_warehouse = secret["SNOWFLAKE_WAREHOUSE"]

        if self.password:
            self.password = urlquote(self.password)
        is_not_dialect_desc = False
        param = None

        logger.info(
            f'SQLAlchemy Dialects will be created for database type: {self.engine_type}')

        if self.engine_type in ["sqlite"]:
            uri = 'sqlite:///' + os.path.join(self.sqlite_db_path,
                                              f"{self.database}.db")
        elif self.engine_type in ["postgres"]:
            uri = (
                f"postgresql+psycopg2://{self.username}:"
                f"{self.password}@{self.host}:{self.port}"
                f"/{self.database}"
            )
            param = dict(client_encoding="utf8")
            is_not_dialect_desc = True
        elif self.engine_type in ["mysql", "mariadb"]:
            uri = (
                f"mysql+pymysql://{self.username}:"
                f"{self.password}@{self.host}:{self.port}"
                f"/{self.database}?charset=utf8mb4"
            )
        elif self.engine_type in ["snowflake"]:
            from snowflake.sqlalchemy import URL
            uri = URL(
                account=self.snowflake_account,
                user=self.username,
                password=self.password,
                database=self.database,
                schema=self.schema,
                warehouse=self.snowflake_warehouse,
                role=self.snowflake_role,
            )
        elif self.engine_type in ["bigquery"]:
            from .cloud.gcp.auth import GcpAuthManager
            gcp_service_file = os.environ.get(
                'GOOGLE_APPLICATION_CREDENTIALS') or None

            gcp_auth = GcpAuthManager(service_accout_file=gcp_service_file)
            project_name = gcp_auth.get_project_name()

            uri = f"bigquery://{project_name}/{self.database}"
            if gcp_service_file:
                param = dict(credentials_path=gcp_service_file)

        return uri, param, is_not_dialect_desc

    def create_session(self):
        """
        Method to create the SQLAlchemy session for the initalized the engine
        type.
        Use the class variables and update to hold the sessions.
        """

        try:
            logger.info(f'Creating SQLAlchemy Dialects session scope.')
            uri, param, is_not_dialect_desc = self.create_uri()
            if param:
                self.engine = create_engine(
                    uri, echo=self.detail_logs, **param)
            else:
                self.engine = create_engine(uri, echo=self.detail_logs)

            if is_not_dialect_desc:
                # https: // github.com/sqlalchemy/sqlalchemy/issues/5645
                self.engine.dialect.description_encoding = None

            self.session = scoped_session(sessionmaker(bind=self.engine))
            logger.info(f'SQLAlchemy Dialects session scope is created')
        except Exception as err:
            logger.exception(
                f'Failed to create session with given paramaters for Database', err)
            traceback.print_tb(err.__traceback__)

            # Propagate the exception
            raise

    def execute_sql(self, sql: str):
        """
        Function to execute DML or DDL queries and return if rows exist.

        ***********
        Attributes:
        -----------

            sql:        (Required) => Plain DDL or DML query to execute on
                        Database.
                        Default is None. One of paramater sql_query or
                        panda_df is required. If both is provided panda_df
                        will be taken as priority and sql_query is ignored.
        *******
        Return:
        -------

            rows:       If rows in case of DML select queries else none.
        """

        rows = None

        db_operation = Operations(self.session)
        rows = db_operation.execute(sql=sql)
        return rows

    def execute_df(self,
                   panda_df: DataFrame,
                   table_name: str,
                   chunk_size: int = None,
                   exist_action: str = "append"):
        """
        Function to execute Pandas DataFrame object to create, replace or
        append table with DataFrame table objects.

        ***********
        Attributes:
        -----------

            panda_df:       (Required) => Pandas DataFrame table object to
                            update the table.
                            Default is None. One of paramater sql_query or
                            panda_df is required. If both is provided panda_df
                            will be taken as priority and sql_query is ignored.
            table_name:     (Optional) => Name of table .
            chunk_size:     (Optional) => chunck size to update the table in
                            chunks for performance rather than insert row one
                            by one.
                            Default: 1 row at a time.
            exist_action:   (Optional) => Action on if table already exist.
                            Default: append mode. Others modes are replace
                            or fail.
        *******
        Return:
        -------

            rows:           If rows in case of DDL queries else none.
        """

        rows = None

        db_operation = Operations(self.session)
        rows = db_operation.execute(panda_df=panda_df,
                                    table_name=table_name,
                                    chunk_size=chunk_size,
                                    exist_action=exist_action)
        return rows

    def get_df(self,
               sql: str,
               chunk_size: int = None):
        """
        Function to execute DML select queries and return Pandas DataFrame
        object.

        ***********
        Attributes:
        -----------

            sql:            (Required) => Plain DDL or DML query to execute on
                            Database.
                            Default is None. One of paramater sql_query or
                            panda_df is required. If both is provided panda_df
                            will be taken as priority and sql_query is ignored.
            chunk_size:     (Optional) => If specified, return an iterator
                            where chunk_size is the number of rows to include
                            in each chunk.
                            Default: None to include all records.
        *******
        Return:
        -------

            rows:           If rows in case of DDL queries else none.
        """

        rows = None

        db_operation = Operations(self.session)
        rows = db_operation.execute(sql=sql,
                                    chunk_size=chunk_size,
                                    get_df=True)
        return rows

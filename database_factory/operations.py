#!/usr/bin/env python

"""
File holds the module to execute the DML or DDL queries on database.
DML queries will automatically get commited as soon as query executed.
"""

import logging
import traceback
import pandas
from pandas import DataFrame
from sqlalchemy.orm import scoped_session
from sqlalchemy import text

logger = logging.getLogger(__name__)


class Operations(object):
    """
    Class handle the Database operation to execute DML or DDL queries.
    Return the rows for DDL and autocommit the table for DML queries.

    ********
    Methods:
    --------

        __init__:   Initaization functions, holds SQLAlchemy session object.

        execute:    Single function to execute DML or DDL queries.
                    Support for Pandas DataFrame object to create, replace
                    or append table with DataFrame table objects.
    """

    def __init__(self, session: scoped_session):
        """
        Initialization function to initlaize the default class object

        ***********
        Attributes:
        -----------

            session:    (Required) => SQLAlchemy session object.
        """

        self.session = session()
        logger.info(
            f'Database operation is initialized for {self.session.bind.name}')

    def execute(self,
                sql: str = None,
                panda_df: DataFrame = None,
                table_name: str = None,
                chunk_size: int = None,
                exist_action: str = "append",
                get_df: bool = False):
        """
        Single function to execute DML or DDL queries. Support for Pandas
        DataFrame object to create, replace or append table with DataFrame
        table objects.

        ***********
        Attributes:
        -----------

            sql:      (Optional) => Plain DDL or DML query to execute on
                            Database.
                            Default is None. One of paramater sql_query or
                            panda_df is required. If both is provided panda_df
                            will be taken as priority and sql_query is ignored.
            panda_df:       (Optional) => Pandas DataFrame table object to
                            update the table.
                            Default is None. One of paramater sql_query or
                            panda_df is required. If both is provided panda_df
                            will be taken as priority and sql_query is ignored.
            table_name:     (Optional) => Name of table used in case of
                            panda_df only.
            chunk_size:     (Optional) => chunck size to update the table in
                            chunks for performance rather than insert row one
                            by one. Used in case of panda_df only.
                            Default: 1 row at a time.
            exist_action:   (Optional) => Action on if table already exist.
                            Used in case of panda_df only.
                            Default: append mode. Others modes are replace
                            or fail.
            get_df:         (Optional) => Execute the DML Select query and
                            return Pandas DataFrame.
                            Default: False to return rows. True will return
                            Pandas Dataframe.
        *******
        Return:
        -------

            rows:           If rows / Pandas Dataframe in case of DDL queries
                            else none.
        """

        rows = None
        try:
            if isinstance(panda_df, DataFrame):
                if len(panda_df):
                    logger.info(
                        f'Got Pandas DataFrame. This will be used to insert data in table.')
                    logger.info(
                        f'Table name: {table_name} and action on table is already present: {exist_action}')
                    logger.info(f'Chunk size to insert data is: {chunk_size}')

                    panda_df.to_sql(name=table_name,
                                    con=self.session.bind,
                                    if_exists=exist_action,
                                    chunksize=chunk_size,
                                    index=False)
                    self.session.commit()
                else:
                    msg = f"Invalid DataFrame"
                    logger.error(msg)
                    raise ValueError(msg)
            elif sql:
                logger.info(f'Got SQL query to execute. Query: {sql}')
                if get_df:
                    rows = pandas.read_sql(sql=sql,
                                           con=self.session.bind,
                                           chunksize=chunk_size)
                else:
                    result = self.session.execute(text(sql))

                    if result.returns_rows:
                        rows = result.fetchall()
                    else:
                        self.session.commit()
            else:
                msg = f"No DDL or DML quesries to execute"
                logger.error(msg)
                raise ValueError(msg)
        except Exception as err:
            logger.exception(f"Failed to execute DDL/DML on database", err)
            traceback.print_tb(err.__traceback__)

            # Propagate the exception
            raise
        finally:
            self.session.close()
        return rows

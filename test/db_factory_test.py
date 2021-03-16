#!/usr/bin/env python

import pytest
import os
import tempfile
from db_factory.manager import DatabaseManager
from db_factory.common.common import Common


def test_db_factory():

    temp_dir = tempfile.gettempdir()

    db_file = os.path.join(temp_dir, "test_db.db")

    os.remove(db_file) if os.path.exists(db_file) else None
    db = DatabaseManager(engine_type="sqlite",
                         database="test_db", sqlite_db_path=temp_dir)
    db.create_session()

    db.execute_sql(sql="create table test (id int PRIMARY KEY)")
    db.execute_sql(sql="insert into test values (1)")
    db.execute_sql(sql="insert into test values (2)")

    assert os.path.exists(db_file) == 1

    rows = db.execute_sql(sql="select * from test")
    assert rows == [(1,), (2,)]

    df = db.get_df(sql="select * from test")
    assert df.values.tolist() == [[1], [2]]

    db.execute_df(panda_df=df, table_name="copy_test", exist_action="replace")
    db.execute_sql(sql="insert into copy_test values (3)")
    rows_copy = db.execute_sql(sql="select * from copy_test")
    assert rows_copy == [(1,), (2,), (3,)]

    dict1 = {"name": "myname", "type": "myposition"}
    dict2 = Common.normaize_connection_dict(
        connection_dict=dict1, is_to_upper=True)
    assert dict2 == {"NAME": "myname", "TYPE": "myposition"}

    dict3 = Common.normaize_connection_dict(connection_dict=dict2)
    assert dict3 == dict1


def test_error_db_factory():
    import os
    temp_dir = tempfile.gettempdir()

    db_file = os.path.join(temp_dir, "test_error.db")

    os.remove(db_file) if os.path.exists(db_file) else None
    db = DatabaseManager(engine_type="sqlite",
                         database="test_error", sqlite_db_path=temp_dir)
    db.create_session()

    db.execute_sql(sql="create table test (id int PRIMARY KEY)")

    try:
        db.execute_sql(sql="insert into test values (asd)")
    except Exception as e:
        assert str(e) == "not all arguments converted during string formatting"

    db2 = DatabaseManager(engine_type="myengine", database="test_error")
    try:
        db2.create_session()
    except Exception as e:
        assert str(e) == "not all arguments converted during string formatting"

    db_file = os.path.join(temp_dir, "test_error.db")
    os.remove(db_file) if os.path.exists(db_file) else None
    db3 = DatabaseManager(engine_type="sqlite", password="y@pwd",
                          database="test_error", sqlite_db_path=temp_dir)
    db3.create_session()
    db3.execute_sql(sql="create table test (id int PRIMARY KEY)")
    db3.execute_sql(sql="insert into test values (1)")
    db3.execute_sql(sql="insert into test values (2)")

    assert os.path.exists(db_file) == 1

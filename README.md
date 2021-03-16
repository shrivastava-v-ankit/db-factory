# db-factory

Database factory is used to manage/create database connection with execute queries using the connection.
The concept of having single source to connect various databases and perform database operations.

User need not to worry on the crafting the connection string and to identify the methods for the database operations.
db-factory supports DML / DDL executions and have support of Pandas DataFrame to create or replace existing tables.

db-factory is wrapper on sqlalchemy for crafting the connection and supports below databases:

```bash
* Sqlite3
* PostgreSQl
* BigQuery
* Snowflake
* MariaDB
* MySQL
```
db-factory can be enhanced for all the sqlalchemy supported database.

## Getting Started

### Setup
------

Assuming that you have Python and virtualenv installed, set up your environment:

#### Setup virtual environment
```bash
$ mkdir $HOME/db-factory
$ cd db-factory
$ virtualenv venv
```
```bash
$ . venv/bin/activate
```

#### Setup from source:
```bash
$ git clone https://github.com/ankit-shrivastava/db-factory.git
$ cd db-factory
$ python -m pip install -e .
```

#### Setup from Github Repository using Pip:
```bash
$ pip install git+https://github.com/ankit-shrivastava/db-factory.git@master
```

#### Setup using build:
```bash
$ git clone https://github.com/ankit-shrivastava/db-factory.git
$ cd db-factory
$ python setup.py bdist_wheel
$ pip install dist/*
```

### Using db-factory
-----
```python
from db_factory.manager import DatabaseManager
import tempfile
temp_dir = tempfile.gettempdir()
db = DatabaseManager(engine_type="sqlite", database="test_db", sqlite_db_path=temp_dir)
db.create_session()

db.execute_sql(sql="create table test (id int PRIMARY KEY)")
db.execute_sql(sql="insert into test values (1)")
db.execute_sql(sql="insert into test values (2)")

rows = db.execute_sql(sql="select * from test")
if rows:
  print(rows)


df = db.get_df(sql="select * from test")
print(df)

db.execute_df(panda_df=df, table_name=copy_test, exist_action="replace")
db.execute_sql(sql="insert into copy_test values (3)")
rows_copy = db.execute_sql(sql="select * from copy_test")
if rows_copy:
  print(rows_copy)
```

## Appendix
### Supported database type:
----
```
*   sqlite `default`
*   postgres
*   mysql
*   mariadb
*   snowflake
```

### Connection parameters for sqlite:
-----
```python
* engine_type: sqlite
* database: <name of database>
* sqlite_db_path: <path where database will be created>
```

### Connection parameters for postgres:
-----
```python
* engine_type: postgres
* database: <name of database>
* username: <postgres user>
* password: <user password>
* host: <host of postgres service>
* port: <port of postgres service>
```

### Connection parameters for mysql:
-----
```python
* engine_type: mysql
* database: <name of database>
* username: <mysql user>
* password: <user password>
* host: <host of mysql service>
* port: <port of mysql servic\>
```

### Connection parameters for mariadb:
-----
```python
* engine_type: mariadb
* database: <name of database>
* username: <mariadb user>
* password: <user password>
* host: <host of mariadb service>
* port: <port of mariadb service>
```

### Connection parameters for snowflake:
-----
```python
* engine_type: snowflake
* database: <name of database>
* username: <snowflake user>
* password: <user password>
* schema: <schema name>
* snowflake_role: <snowflake role>
* snowflake_warehouse: <snowflake warehouse>
* snowflake_account: <snowflake account>
```

### Connection parameters for bigquery:
-----
```python
* engine_type: bigquery
* database: <name of database>
```

### Getting connection properties from AWS / GCP Secret Manager Service:
-----
Note:
* GCP: 
   * On Cloud Server:
       * Set server to execute the all cloud api services
       * Attach following permissions
          * Project Viewer
          * Secret Manager Secret Accessor
   * On Premises:
       * Attach following permissions to user service account and download service account file for authentication:
          * Project Viewer
          * Secret Manager Secret Accessor
       * Set environment variable "GOOGLE_APPLICATION_CREDENTIALS" pointing to service account file.
* AWS:
   * On Cloud Server:
      * Set execution profile with "secretsmanager:GetSecretValue" policy
   * On Premises:
      * AWS should be configured
      * User should have permissions of "secretsmanager:GetSecretValue" policy.

```python
* engine_type: bigquery
* database: <name of database>
* secret_id: <Secret name of AWS / GCP Secret Manager Service>
* secrete_manager_cloud: <aws or gcp as per cloud>
* aws_region: <aws region: default=> us-east-1>
```

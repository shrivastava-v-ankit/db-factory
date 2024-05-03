# database-factory

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI](https://img.shields.io/pypi/v/database-factory.svg)](https://pypi.org/project/database-factory)
[![CircleCI](https://circleci.com/gh/shrivastava-v-ankit/database-factory.svg?style=svg)](https://circleci.com/gh/shrivastava-v-ankit/database-factory)



Database factory is used to manage/create database connection with execute queries using the connection.
The concept of having single source to connect various databases and perform database operations.

User need not to worry on the crafting the connection string and to identify the methods for the database operations.
Database factory supports DML / DDL executions and have support of Pandas DataFrame to create or replace existing tables.

Database factory is wrapper on sqlalchemy for crafting the connection and supports below databases:

```bash
* Sqlite3
* PostgreSQl
* BigQuery
* Snowflake
* MariaDB
* MySQL
```
Database factory can be enhanced for all the sqlalchemy supported database.

## Getting Started

```bash
pip install database-factory
```
Note: Default installation for database factory is to support Sqlite3. For other database/cloud support it can be installed with compinations of extra libraries

### Sqite3 with AWS cloud support
```bash
pip install database-factory["aws"]
```

### Snowflake with AWS cloud support
```bash
pip install database-factory["snowflake,aws"]
```

### Following options are supported
   * Secret manager cloud support
      * aws
      * gcp
   * Databases
      * snowflake
      * postgres
      * mysql
   * all: Will install with libraries of all supported cloud and supported databases.

### Using database-factory
-----
```python
from database_factory.manager import DatabaseManager
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
# db.execute_df(panda_df=df, table_name=copy_test, exist_action="replace", chunk_size=100)
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


### Development Setup

#### Using virtualenv

```bash
python3 -m venv venv
source env/bin/activate
pip install .
```

### Contributing

1. Fork repo- https://github.com/shrivastava-v-ankit/database-factory.git
2. Create your feature branch - `git checkout -b feature/name`
3. Install Python packages
   * sqlalchemy==1.4.47
   * pandas==1.5.3
   * GitPython
   * coverage==7.2.3
   * exceptiongroup==1.1.1
   * iniconfig==2.0.0
   * pluggy==1.0.0
   * pytest==7.3.0
   * pytest-cov==4.0.0
   * tomli==2.0.1
4. Run Python test (pytest)
   * pytest -v --cov --cov-report html --cov-report xml --junitxml=test-results/database_factory_test/results.xml
5. Add Python test (pytest) and covrage report for new/changed feature.
4. Commit your changes - `git commit -am "Added name"`
5. Push to the branch - `git push origin feature/name`
6. Create a new pull request


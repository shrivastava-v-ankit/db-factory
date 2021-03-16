#!/usr/bin/env python

"""
Prerequesites -
  Python Packages:
    * setuptools
    * GitPython
  System Packages:
    * make
    * Python 3
Commands: python setup.py [bdist_wheel / [sdist [--format=[gztar][,tar]]]
Ex:
  * python setup.py bdist_wheel
  * python setup.py sdist
  * python setup.py sdist --format=gztar
  * python setup.py sdist --format=tar
  * python setup.py sdist --format=gztar,tar
  * python setup.py sdist --format=gztar
  * python setup.py bdist_wheel sdist --format=gztar,tar
"""

"""
distutils/setuptools install script.
"""


from setuptools import setup, find_packages
import traceback
import shutil
import re
import os
__NAME__ = "database-factory"

ROOT = os.path.dirname(os.path.abspath(__file__))
VERSION_FILE = os.path.join(ROOT, __NAME__.replace("-", "_"), ".version")
VERSION_RE = re.compile(r'''__version__ = ['"]([0-9.]+)['"]''')

base = [
    "sqlalchemy-utils",               # Various utility functions for SQLAlchemy
    "pandas",                         # Powerful data structures for data analysis,
                                      # time series, and statistics
    "numpy"                           # NumPy is the fundamental package for array
                                      # computing with Python.
]

aws = [
    "boto3"                           # The AWS SDK for Python
]

gcp = [
    "google-cloud-bigquery",          # Google BigQuery API client library
    "google-api-python-client",       # Google API Client Library for Python
    "google-cloud-bigquery-storage",  # Google BigQuery Storage API client library
    "google-cloud-secret-manager",    # Google Secret Manager API API client library
    "google-cloud-resource-manager",  # Google Cloud Resource Manager API client lib
    "pybigquery",                     # SQLAlchemy dialect for BigQuery
    "pyarrow"                         # Python library for Apache Arrow
]

snowflake = [
    "snowflake-connector-python",     # Snowflake Connector Library
    "snowflake-sqlalchemy",           # Snowflake SQLAlchemy Dialect
    "requests==2.23.0"                # Python HTTP for Humans.
]

postgres = [
    "pg8000"                          # PostgreSQL interface library.
]

mysql = [
    "pymysql"                         # Pure Python MySQL Driver
]

setups = []

ir = (base + aws + gcp + snowflake + postgres + mysql)
requires = ir


def delete(path):
    if os.path.exists(path=path):
        try:
            if os.path.isfile(path=path):
                os.remove(path=path)
            else:
                shutil.rmtree(path=path)
        except:
            pass


def write_version(version, sha, filename):
    text = f"__version__ = '{version}'\n__REVESION__ = '{sha}'"
    with open(file=filename, mode="w") as file:
        file.write(text)


def get_version(filename):
    version = "1.0.0"  # Adding default version

    # This block is for reading the version from foundry distribution
    if os.path.exists(path=filename):
        contents = None
        with open(file=filename, mode="r") as file:
            contents = file.read()
            version = VERSION_RE.search(contents).group(1)
            return version

    # If file not found. Then may be local or want to get the version
    version_python_file = os.path.join(ROOT, "version.py")
    if os.path.exists(path=version_python_file):
        import version as ver
        version = ver.version

        sha = ""
        try:
            import git
            repo = git.Repo(path=".", search_parent_directories=True)
            sha = repo.head.commit.hexsha
            sha = repo.git.rev_parse(sha, short=6)
        except ImportError:
            print(f"Import error on git, can be ignored for build")
            pass
        except Exception as exception:
            print(str(exception))
            traceback.print_tb(exception.__traceback__)
            pass
        write_version(version=version, sha=sha, filename=filename)
    return version


with open("README.md", "r") as f:
    long_description = f.read()


def do_setup():
    setup(
        name=__NAME__,
        version=get_version(filename=VERSION_FILE),
        description="Database Factory;",
        long_description=long_description,
        long_description_content_type="text/markdown",
        keywords=['python', 'os independent', 'database', 'sqlalchemy',
                  'sqlite3', 'sqlite', 'postgres', 'mysql', 'maridb',
                  'snowflake', 'bigquery', 'secret manager'],
        author="Ankit Shrivastava",
        url="https://github.com/shrivastava-v-ankit/database-factory",
        packages=find_packages(include=[__NAME__.replace("-", "_")]),
        include_package_data=True,
        setup_requires=setups,
        install_requires=requires,
        license="MIT",
        python_requires=">=3.4",
        platforms='any',
        project_urls={
            'Source': 'https://github.com/shrivastava-v-ankit/database-factory/',
            'Tracker': 'https://github.com/shrivastava-v-ankit/database-factory/issues',
        },
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'Natural Language :: English',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Software Development :: Version Control :: Git',
        ],
    )


if __name__ == "__main__":
    import sys

    do_setup()

    if "sdist" in sys.argv or "bdist_wheel" in sys.argv:
        egg_info = os.path.join(ROOT, __NAME__.replace("-", "_") + '.egg-info')
        delete(path=egg_info)
        eggs = os.path.join(ROOT, ".eggs")
        delete(path=eggs)
        delete(path=VERSION_FILE)
        build_dir = os.path.join(ROOT, "build")
        delete(path=build_dir)

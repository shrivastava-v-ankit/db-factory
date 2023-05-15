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
    # Database Abstraction Library
    "sqlalchemy==1.4.47",
    # Powerful data structures for data analysis, time series, and statistics
    "pandas==1.5.3"

]

aws = [
    # The AWS SDK for Python
    "boto3==1.26.113"
]

gcp = [
    # This library simplifies using Google’s various server-to-server authentication mechanisms to access Google APIs.
    "google-auth==2.17.3",
    # This library provides an httplib2 transport for google-auth.
    "google-auth-httplib2==0.1.0",
    # Google BigQuery API client library
    "google-cloud-bigquery==3.9.0",
    # Google API Client Library for Python
    "google-api-python-client==2.85.0",
    # Google Secret Manager API API client library
    "google-cloud-secret-manager==2.16.1",
    # Google Cloud Resource Manager API client lib
    "google-cloud-resource-manager==1.9.1",
    # SQLAlchemy dialect for BigQuery
    "pybigquery==0.10.2"
]

snowflake = [
    # Snowflake Connector Library
    "snowflake-connector-python==2.7.9",
    # Snowflake SQLAlchemy Dialect
    "snowflake-sqlalchemy==1.4.7"
]

postgres = [
    # PostgreSQL interface library.
    "pg8000==1.29.4"
]

mysql = [
    # Pure Python MySQL Driver
    "pymysql==1.0.3"
]

dependencies = [
    "asn1crypto==1.5.1",
    "botocore==1.29.113",
    "cachetools==5.3.0",
    "certifi==2022.12.7",
    "cffi==1.15.1",
    "charset-normalizer==2.0.12",
    "cryptography==36.0.2",
    "future==0.18.3",
    "google-api-core==2.11.0",
    "google-cloud-bigquery-storage==2.19.1",
    "google-cloud-core==2.3.2",
    "google-crc32c==1.5.0",
    "google-resumable-media==2.4.1",
    "googleapis-common-protos==1.59.0",
    "greenlet==2.0.2",
    "grpc-google-iam-v1==0.12.6",
    "grpcio==1.53.0",
    "httplib2==0.22.0",
    "idna==3.4",
    "jmespath==1.0.1",
    "numpy==1.24.2",
    "oscrypto==1.3.0",
    "packaging==23.1",
    "proto-plus==1.22.2",
    "protobuf==3.20.3",
    "pyarrow==6.0.1",
    "pyasn1==0.4.8",
    "pyasn1-modules==0.2.8",
    "pycparser==2.21",
    "pycryptodomex==3.17",
    "pyjwt==2.6.0",
    "pymysql==1.0.3",
    "pyopenssl==22.0.0",
    "pyparsing==3.0.9",
    "python-dateutil==2.8.2",
    "pytz==2023.3",
    "requests==2.28.2",
    "rsa==4.9",
    "s3transfer==0.6.0",
    "scramp==1.4.4",
    "six==1.16.0",
    "uritemplate==4.1.1",
    "urllib3==1.26.15"
]

setups = []

ir = (base + aws + gcp + snowflake + postgres + mysql + dependencies)
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
        python_requires=">=3.7, <4",
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
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
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

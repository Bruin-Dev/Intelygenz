import sys
from setuptools import setup, find_packages

NAME = "igzpackages"
VERSION = "0.0.1"

REQUIRES = [
    # Core dependencies
    "async-timeout == 3.0.1",
    "asyncio == 3.4.3",
    "asyncio-nats-client == 0.9.2",
    "asynctest == 0.12.2",
    "nats-python==0.4.0",
    "pytest==5.2.0",
    "pytest-asyncio==0.10.0",
    "pytest-cov==2.7.1",
    "coverage == 4.5.4",
    "Quart==0.6.15",
    "quart-openapi==1.4.3",
    "behave == 1.2.6",
    "tenacity == 5.0.4",
    "shortuuid==0.5.0",
    "multidict==4.6.1",
    "redis==3.3.11",
    "python-dateutil==2.8.1",
    "pytz==2018.3",
    # Transitive dependencies
    "aiofiles==0.8.0",
    "atomicwrites==1.4.0",
    "attrs==21.3.0",
    "blinker==1.4",
    "click==8.0.3",
    "dataclasses==0.8",
    "h11==0.8.1",
    "h2==4.1.0",
    "hpack==4.0.0",
    "Hypercorn==0.5.4",
    "hyperframe==6.0.1",
    "importlib-metadata==4.8.1",
    "itsdangerous==2.0.1",
    "Jinja2==3.0.3",
    "jsonschema==2.6.0",
    "MarkupSafe==2.0.1",
    "more-itertools==8.12.0",
    "packaging==21.3",
    "parse==1.19.0",
    "parse-type==0.5.2",
    "pluggy==0.13.1",
    "py==1.11.0",
    "pyparsing==3.0.6",
    "pytoml==0.1.21",
    "six==1.16.0",
    "sortedcontainers==2.4.0",
    "typing_extensions==4.0.1",
    "wcwidth==0.2.5",
    "wsproto==0.15.0",
    "zipp==3.6.0",
]
setup(
    name=NAME,
    version=VERSION,
    description='IGZ\'s utilities for Automation-Engine project',
    author='Intelygenz',
    author_email='mettel@intelygenz.com',
    url='http://s3pypi.mettel-automation.net.s3.amazonaws.com/igzpackages/index.html',
    install_requires=REQUIRES,
    packages=find_packages(exclude=['*tests']),
    include_package_data=True,
    setup_requires=[
        'pytest-runner',
    ],
    test_suite='test.unittest'
)

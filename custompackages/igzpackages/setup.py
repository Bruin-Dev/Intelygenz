import sys
from setuptools import setup, find_packages

NAME = "igzpackages"
VERSION = "0.0.1"

REQUIRES = ["asgiref == 2.3.2",
            "async-timeout == 3.0.1",
            "asyncio == 3.4.3",
            "asyncio-nats-client == 0.8.2",
            "asyncio-nats-streaming == 0.1.2",
            "asynctest == 0.12.2",
            "atomicwrites == 1.3.0",
            "attrs == 18.2.0",
            "coverage == 4.5.2",
            "dataclasses==0.6",
            "more-itertools==6.0.0",
            "nats-python==0.4.0",
            "pluggy==0.8.1",
            "protobuf==3.6.1",
            "protobuf==3.6.1",
            "py==1.7.0",
            "pytest==4.2.1",
            "pytest-asyncio==0.10.0",
            "pytest-cov==2.6.1",
            "six==1.12.0",
            ]
setup(
    name=NAME,
    version=VERSION,
    description='IGZ\'s utilities for Automation-Engine project',
    install_requires=REQUIRES,
    packages=find_packages(exclude=['*tests']),
    include_package_data=True,
    setup_requires=[
        'pytest-runner',
    ],
    test_suite='test.unittest'
)

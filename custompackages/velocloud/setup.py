# coding: utf-8

"""
    Velocloud API

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)

    OpenAPI spec version: 3.2.19

    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import sys
from setuptools import setup, find_packages

NAME = "velocloud"
VERSION = "3.2.19"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["urllib3 >= 1.15",
            "six >= 1.10",
            "certifi",
            "python-dateutil",
            "pytest==4.2.1",
            "pytest-cov==2.6.1",
            "coverage == 4.5.2"
            ]

setup(
    name=NAME,
    version=VERSION,
    description="Velocloud API",
    author_email="",
    url="",
    keywords=["Swagger", "Velocloud API"],
    install_requires=REQUIRES,
    packages=find_packages(exclude=['*tests']),
    include_package_data=True,
    setup_requires=[
        'pytest-runner',
    ],
    test_suite='test.unittest',
    long_description="""\
    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)
    """
)

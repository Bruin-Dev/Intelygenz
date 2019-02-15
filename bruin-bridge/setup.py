# This will be executed everytime we make a pip install

# TODO take a look in case we can automate the requirements.txt in a "dependencies" block in this file
from setuptools import setup, find_packages
setup(
    name='bruin-bridge',
    version='1.0.0',
    description='MetTel\'s automation bridge/adapter for Bruin system',
    packages=find_packages(exclude=['*tests']),
    include_package_data=True,
    setup_requires=[
        'pytest-runner',
    ],
    test_suite='test.unittest'
)
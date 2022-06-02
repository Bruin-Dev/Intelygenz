# This will be executed everytime we make a pip install
# The find_packages is very important since it's used to make all our packages visible to each other inside the project

from setuptools import find_packages, setup

setup(
    name="hawkeye-outage-monitor",
    version="1.0.0",
    description="MetTel's automation service outage monitor for Hawkeye",
    packages=find_packages(exclude=["*tests"]),
    include_package_data=True,
    setup_requires=[
        "pytest-runner",
    ],
    test_suite="test.unittest",
)

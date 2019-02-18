# Table of contents
- [Getting started](#getting-started)
- [Adding new libraries to the project](#adding-new-libraries-to-the-project)
- [Fast development in local environment](#fast-development-in-local-environment)
- [Testing](#testing)
  * [Develop new tests](#develop-new-tests)
  * [Coverage configuration](#coverage-configuration)
- [Technologies used](#technologies-used)
- [Useful documentation](#useful-documentation)

# Getting started
- Install python 3
- Install pip for python 3
- Install virtualenv for python 3

Then create and activate the virtualenv like this:
````
python3 -m venv env
source ./env/bin/activate
pip install -r requirements.txt
````

# Adding new libraries to the project

With virtualenv activated

````
pip install some-package
pip freeze | grep -v "pkg-resources" > requirements.txt #The grep -v is needed only if you use Ubuntu due a harmless bug
````
Remember to commit the new requirements.txt file


# Fast development in local environment

- [JUST ONCE] Go to /etc/hosts and add ``127.0.0.1	nats-streaming``
- Go to project root
- Type the following ``docker-compose up nats-streaming``

Now you can execute your python code related to NATS connections, using nats-streaming as host name

# Testing
This project uses pytest, you can find more information in the [Useful documentation section](#useful-documentation)
## Develop new tests
Conventions for files, classes and functions can be found in the [pytest.ini file](pytest.ini)

## Coverage configuration
Coverage is configured in the [.coveragerc file](.coveragerc)

# Technologies used

- [Asyncio nats streaming](https://github.com/nats-io/asyncio-nats-streaming)
- [ASGI library for async](https://pypi.org/project/asgiref/)

# Useful documentation
- [Python async simplified with asgiref and asyncio](https://www.aeracode.org/2018/02/19/python-async-simplified/)
- [Getting started with testing in Python](https://realpython.com/python-testing/#choosing-a-test-runner)
- [Pytest documentation](https://docs.pytest.org/en/latest/getting-started.html)
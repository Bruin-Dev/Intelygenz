# Table of contents
- [Workflow](#workflow)
  * [Get an instance of NATS cluster up in local environment](#get-an-instance-of-nats-cluster-up-in-local-environment)
  * [Configuration, environment variables and configuration files](#configuration-environment-variables-and-configuration-files)
  * [Testing](#testing)
  * [Adding new libraries to the project](#adding-new-libraries-to-the-project)
- [Technologies used](#technologies-used)
- [Useful documentation](#useful-documentation)

# Workflow
- Install python 3.6
- Install pip for python 3.6
- Install virtualenv for python 3.6
- Add the [precommit hook for PEP8](https://github.com/cbrueffer/pep8-git-hook) to automation-engine/.git/hooks/

Then create and activate the virtualenv like this:
````
python3 -m venv base-microservice-env
source ./base-microservice-env/bin/activate
pip install -r requirements.txt
````
## Get an instance of NATS cluster up in local environment

- [JUST ONCE] Go to /etc/hosts and add ``127.0.0.1	nats-streaming``
- Go to project root
- Type the following ``docker-compose up nats-streaming``

Now you can execute your python code related to NATS connections, using nats-streaming as host name


## Configuration, environment variables and configuration files
Some of the configuration parameters can change between environments.
That's why the config module is there: a centralized file to keep both environment and constant parameters
needed for our service to work.

The [.template.env](/src/config/.template.env) file is an example, without values, of all the parameters from environment variables the service needs to work.
You should ask for an env file to place under the config folder. That file should have the values of the environments variables set.

Make sure you use `source env` from the config directory or that **you point pycharm what env file to use before execute the service**

The module [config](src/config/config.py) loads in a map all variables from the environment before each execution. If any is not present, the service won't get up and running.
The module [testconfig](src/config/testconfig.py) loads values in a map that is the same as the [config module](src/config/config.py) one, but the values are **NEVER FETCHED FROM ENVIRONMENT VARIABLES** that way we keep our pipelines of unit tests clean.

## Testing
Currently we are working with pytest.
The test configurations can be found in the files [pytest.ini](pytest.ini) and [.coveragerc](.coveragerc)

For writing new tests you must replicate the application directory folder structure inside the test folder.

So we have something like
    - application
        - somepackage
            - somemodule.py
    - tests
        -somepackage
            -somemodule_test.py
            
Test files put under tests directory will be auto-discovered by pytest as long as their module name ends with *_test.py
To run the test suite of a service, navigate to the root of the project (in this case, bruin-bridge) and type `pytest --cov` in a shell.
Pycharm can also be easily configured for that purpose, in order to debug tests.

## Adding new libraries to the project

With virtualenv activated

````
pip install some-package
pip freeze | grep -v "pkg-resources" > requirements.txt #The grep -v is needed only if you use Ubuntu due a harmless bug
````
**Remember to commit the new requirements.txt file**

**VERY IMPORTANT: If the microservice is using any custompackages, change any line related with them after each pip freeze for a relative import. I.E: If you are using velocloud package, change `velocloud==3.2.19` line to `../custompackages/velocloud`**

# Technologies used

- [Asyncio nats streaming](https://github.com/nats-io/asyncio-nats-streaming)
- [ASGI library for async](https://pypi.org/project/asgiref/)

# Useful documentation
- [Python async simplified with asgiref and asyncio](https://www.aeracode.org/2018/02/19/python-async-simplified/)
- [Getting started with testing in Python](https://realpython.com/python-testing/#choosing-a-test-runner)
- [Pytest documentation](https://docs.pytest.org/en/latest/getting-started.html)
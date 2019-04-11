# Table of contents
- [Introduction](#introduction)
- [Workflow](#workflow)
  * [Get an instance of NATS cluster up in local environment](#get-an-instance-of-nats-cluster-up-in-local-environment)
  * [Configuration, environment variables and configuration files](#configuration--environment-variables-and-configuration-files)
  * [Run acceptance tests for a sub project](#run-acceptance-tests-for-a-sub-project)
  * [Run/Debug acceptance tests for a sub project in PyCharm](#run-debug-acceptance-tests-for-a-sub-project-in-pycharm)
  * [Create or edit Features or Scenarios](#create-or-edit-features-or-scenarios)
  * [Create acceptance tests for a new sub project](#create-acceptance-tests-for-a-new-sub-project)
- [Technologies used](#technologies-used)
- [Useful documentation](#useful-documentation)

# Introduction
This is the repository to hold the acceptance tests for every sub project.

To do so, CI pipeline is using [behave](https://behave.readthedocs.io/en/latest/) which will generate a json report for every subproject that 
will be sent to [HonestCode](http://pro.honestcode.io).
It is necessary to read [HonestCode documentation](https://honestcode.io/introduction-to-honestcode/) before updating project from within the platform.

# Workflow
- Install python 3.6
- Install pip for python 3.6
- Install virtualenv for python 3.6
- Add the [precommit hook for PEP8](https://github.com/cbrueffer/pep8-git-hook) to automation-engine/.git/hooks/

Then, we need to create and activate its virtualenv for every sub project we want to run acceptance tests for, like this:
````
cd <folder-name>
python3 -m venv acc-tests-<folder-name>-env
source ./acc-tests-<folder-name>-env/bin/activate
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

If you have an env file of the sub project you want to run acceptance tests for, place it in acceptance-tests/<project-folder>/config folder. If not, you should ask for it. That file should have the values of the environments variables set.
To use it from local environment, you should use `export` before variables definitions.

Make sure you use `source env` from the config directory or that **you point pycharm what env file to use before executing the service**


The module `config` loads in a map all variables from the environment before each execution. If any is not present, the service won't get up and running.
The module `testconfig` loads values in a map that is the same as the `config` one, but the values are **NEVER FETCHED FROM ENVIRONMENT VARIABLES** that way we keep our pipelines of acceptance tests clean.

## Run acceptance tests for a sub project
Currently we are using behave.

Features and Steps inside a sub project folder will be auto discovered by behave, so just run:
```
cd acceptance-tests/<sub-project-folder>/ && behave src
```

## Run/Debug acceptance tests for a sub project in PyCharm
1. Create a new Run/debug configuration.
2. Set up a name for it, referencing the feature you want to run.
3. Configuration -> `Script path`: The absolute path to the behave library main module, something like this:
```<absolute-path-to-env-folder>/lib/python3.6/site-packages/behave/__main__.py```
4. Configuration -> `Parameters`: Absolute path to the .feature file we want to run.
5. Configuration -> `Working directory`: The absolute path to the behave library folder, something like this:
```<absolute-path-to-env-folder>/lib/python3.6/site-packages/behave/```
6. EnvFile -> Select the .env file for the sub project.

## Create or edit Features or Scenarios
*Due to HonestCode integration, we should not change any file in `features` directory, because it is going to be overwritten every time we publish the blueprint in HonestCode.*

We just can develop steps for Scenarios already created in HonestCode.
To create a new one:
- Keep in mind these [considerations](https://honestcode.io/faqs/) before creating a new Scenario.
- Define test scenarios and features and press "Publish now" to update feature files in repository.

Get last changes from repository and now you can code new steps.

## Create acceptance tests for a new sub project

- For code, follow this structure:
```
acceptance-tests/
    ...
    <subproject-name>/
        src/
            config/...
            features/
            steps/
        requirements.txt
```
- In HonestCode:
    * Create a new Blueprint pointing features to your features folder, and set up remote repository configuration.
    * Create your features and scenarios.
    * Publish the blueprint and pull new generated `.feature` files from repository.

# Technologies used

- [Asyncio nats streaming](https://github.com/nats-io/asyncio-nats-streaming)
- [ASGI library for async](https://pypi.org/project/asgiref/)
- [Behave for python](https://pypi.org/project/behave/)

# Useful documentation
- [Python async simplified with asgiref and asyncio](https://www.aeracode.org/2018/02/19/python-async-simplified/)
- [Getting started with testing in Python](https://realpython.com/python-testing/#choosing-a-test-runner)
- [Behave documentation](https://behave.readthedocs.io/en/latest/tutorial.html#features)
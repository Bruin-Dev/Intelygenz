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
Follow instructions described in [base-microservice](../base-microservice/README.md) to:
* Get an instance of NATS cluster up in local environment.
* Configuration, environment variables and configuration files.

## Run acceptance tests for a sub project
Currently we are using behave.

Features and Steps inside a sub project folder will be auto discovered by behave, so just run:
```
cd acceptance-tests/<sub-project-folder>/ && behave src
```
To run acceptance tests in local environment and see results in HonestCode, you can do the following:
* Export the BLUEPRINT env variable with the blueprint key you want to run tests for:
```.bash
export BLUEPRINT=blueprint/bp....
```
* Build and run docker-compose this way:
```bash
docker-compose -f docker-compose-ci.yml up --build --abort-on-container-exit
```
* Results of execution are shown on your terminal and HonestCode app.

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

- [Asyncio nats client](https://github.com/nats-io/asyncio-nats)
- [Behave for python](https://pypi.org/project/behave/)

# Useful documentation
- [Behave](https://behave.readthedocs.io/en/latest/tutorial.html#features)
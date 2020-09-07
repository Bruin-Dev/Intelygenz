# Dispatch Portal(Backend) API

This microservice will unify the dispatch operations over N remote APIs:

- LIT
- CTS

# Table of contents
- [Workflow](#workflow)
  * [Get an instance of NATS cluster up in local environment](#get-an-instance-of-nats-cluster-up-in-local-environment)
  * [Swagger & Schema](#swagger--schema)
  * [Configuration, environment variables and configuration files](#configuration-environment-variables-and-configuration-files)
  * [Testing](#testing)
  * [Adding new libraries to the project](#adding-new-libraries-to-the-project)
- [Vendors](#vendors)
  * [LIT](#vendor--lit)
  * [CTS](#vendor--cts)
- [Bruin](#bruin-bridge)
- [Technologies used](#technologies-used)
- [Useful documentation](#useful-documentation)

# Workflow
- Install python 3.6
- Install pip for python 3.6
- Install virtualenv for python 3.6
- Add the [precommit hook for PEP8](https://github.com/cbrueffer/pep8-git-hook) to automation-engine/.git/hooks/

Then create and activate the virtualenv like this:

```
python3 -m venv dispatch-portal-backend-env
source ./dispatch-portal-backend-env/bin/activate
pip install -r requirements.txt
```

## Get an instance of NATS cluster, redis, lit-bridge, cts-bridge and dispatch-portal-backend

```bash
# env file
NATS_SERVER1=nats://nats-server:4222
REDIS_HOSTNAME=redis
DISPATCH_PORTAL_SERVER_PORT=5000
```

- Type the following ``docker-compose up --build nats-server redis lit-bridge dispatch-portal-backend``

Local development and debugging

```bash
cd dispatch-portal-backend/src
export NATS_SERVER1="nats://localhost:4222"
export REDIS_HOSTNAME="localhost"
export DISPATCH_PORTAL_SERVER_PORT=5004
python app.py
```

## Swagger & Schema

To achieve validation we use the schema, and to generate the schema we create de swagger.
To generate the schema from the swagger, we need to go to this url: `http://127.0.0.1:5000/api/doc/swagger.json`, 
then copy the content to the file `schema.json`.
At this point the self-generated openapi schema.json from the library `quart-openapi` is not working.
So we are using the following library `swagger-ui-py`.

To see the API definition:

- Swagger file: [swagger.yml](<./src/swagger.yml>)

To check the schema:

- Schema file: [schema.json](<./src/schema.json>)

## Configuration, environment variables and configuration files
Some of the configuration parameters can change between environments.
That's why the config module is there: a centralized file to keep both environment and constant parameters
needed for our service to work.

The [.template.env](/src/config/.template.env) file is an example, without values, of all the parameters from environment variables the service needs to work.
You should ask for an env file to place under the config folder. That file should have the values of the environment variables set.

Make sure you use `source env` from the config directory or that **you point pycharm what env file to use before execute the service**
To use it from local environment execution, you should write `export` before each variable definitions.

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

# Vendors

At this moment we only support 2 vendors LIT and CTS. All the credentials for the different environments are in 1password.

Exists 2 mappers, one for each vendor so we can customize the response for the frontend.

All the notes and email are created through templates (in the future should be nice to change all to jinja2)

## LIT

We have 2 environments, one for testing and production.

This communicates with `lit-bridge` and `dispatch-portal-frontend`.

The endpoints this vendor accept are the following:

- Get all dispatches - GET - `/lit/dispatch`
- Get single dispatch - GET - `/lit/dispatch/<dispatch_number>`
- Create new dispatch - POST - `/lit/dispatch`
    - we create the dispatch and we get a dispatch number like `S-12345`
- Cancel single dispatch - DELETE - `/lit/dispatch/<dispatch_number>`
    - we send an email with the dispatch we want to cancel to: `dispatch@litnetworking.com`
- Update single dispatch - POST - `/lit/dispatch`
- Upload file to dispatch (implemented but never tested or used in production) - POST - `/lit/dispatch/<dispatch_number>/upload_file`

## CTS

We only have production environment for this vendor.

This communicates with `cts-bridge` and `dispatch-portal-frontend`.

The endpoints this vendor accept are the following:

- Get all dispatches - GET - `/cts/dispatch`
- Get single dispatch - GET - `/cts/dispatch/<dispatch_number>`
- Create new dispatch - POST - `/cts/dispatch`
    - To create the dispatch we send an email request to: `CTS-MettelService@core-techs.com`, for testing we should change it.
    - In that email request we attach all the info about the dispatch and an UUID generated by us (format: IGZXXXXXXXXXXXXXXXX), and that UUID will be the main ID during the rest of the processes. 
- Cancel single dispatch - DELETE - `/cts/dispatch/<dispatch_number>`
    - we send an email with the dispatch we want to cancel to the same email as create.

# Bruin

To fill the address fields and client name during creating a new dispatch

- **GET /bruin/ticket_address/{ticket_id}**

Response:

```json
# GET /bruin/ticket_address/{ticket_id}
{
  'client_name': "Red Rose",
  'client_address': {
    'address': '123 Fake Street',
    'city': 'Pleasantown',
    'state': 'CA',
    'zip': '99088',
    'country': 'United States'
  }
}
```

# Technologies used

- [Asyncio nats client](https://github.com/nats-io/asyncio-nats)
- [ASGI library for async](https://pypi.org/project/asgiref/)
- [ASGI library for quart](https://pgjones.gitlab.io/quart/)
- [Quart openapi](https://github.com/factset/quart-openapi)
- [Swagger UI](https://pypi.org/project/swagger-ui-py/)

# Useful documentation
- [Python async simplified with asgiref and asyncio](https://www.aeracode.org/2018/02/19/python-async-simplified/)
- [Getting started with testing in Python](https://realpython.com/python-testing/#choosing-a-test-runner)
- [Pytest documentation](https://docs.pytest.org/en/latest/getting-started.html)
- [SwaggerUI Quart](https://medium.com/@hkaraoguz/using-swaggerui-with-quart-72a3dab19273)

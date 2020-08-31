# Service Dispatch Monitor

# Dispatch Monitor for LIT and CTS
This microservice will unify the dispatch operations over N remote APIs:

- LIT Monitor
- CTS Monitor

# Table of contents
- [Workflow](#workflow)
  * [Get an instance of NATS cluster up in local environment](#get-an-instance-of-nats-cluster-up-in-local-environment)
  * [Dispatch Monitor](#dispatch--monitor)
    - [LIT Monitor](#lit--monitor)
    - [CTS Monitor](#cts--monitor)
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

```
python3 -m venv dispatch-portal-backend-env
source ./dispatch-portal-backend-env/bin/activate
pip install -r requirements.txt
```

## Get an instance of NATS cluster, redis, notifier, lit-bridge, and cts-bridge

```bash
# env file
NATS_SERVER1=nats://nats-server:4222
REDIS_HOSTNAME=redis
DISPATCH_PORTAL_SERVER_PORT=5000
```

- Type the following ``docker-compose up --build nats-server redis notifier cts-bridge lit-bridge service-dispatch-monitor``

Local development and debugging

```bash
cd service-dispatch-monitor/src
export NATS_SERVER1="nats://localhost:4222"
export REDIS_HOSTNAME="localhost"
export DISPATCH_PORTAL_SERVER_PORT=5004
python app.py
```

## Dispatch Monitor

This microservice monitor dispatches statuses for different vendors, at the time of writting this document LIT and CTS. Both processes are pretty much the same in concept but with differences in the implementation.

A dispatch is general terms can have the following statuses:

- Requested
- Confirmed
- Tech on site
- Canceled
- Completed

The following table will show how match them with the vendors:

| Vendor  |  General Status | Status  |
|---|---|---|
| LIT  | Requested | New Dispatch |
| LIT  | Confirmed | Request Confirmed |
| LIT  | Tech on site | Tech Arrived |
| LIT  | Canceled | Cancelled |
| LIT  | Completed | Close Out  |
| CTS  | Requested | Open |   |   |
| CTS  | Confirmed | Scheduled |
| CTS  | Tech on site | On Site |
| CTS  | Canceled | Canceled |
| CTS  | Completed | Completed |
| CTS  | Completed | Complete Pending Collateral |

The main use is to monitor:

- Dispatch status changed
- Updates in the dispatch like the technician
- Send sms prior 2 and 12 hours before
- Send sms tech on site
- Cancel dispatch (Both send an email request)

The basic algorithm behaves like this:

- Get all dispatches for a vendor
- Filter dispatches that are created through the `dispatch-portal`
- Discard invalid ticket ids or dispatches with not proper fields
- Split the dispatches by status and then send them to the function to proccess them, there are 3 general functions
    * Confirmed dispatch:
        - Send sms and append note to bruin when a dispatch is confirmed
        - Send sms and append note to bruin 12 or 2 hours prior the dispatch
        - Send sms and append note to bruin when a tech has changed
    * Tech on site dispatch:
        - Send sms and append note to bruin when tech on site
    * Canceled dispatch:
        - Append note to bruin when a dispatch is canceled

Both vendors have the same structure, and the fields differ the way we do some actions.

LIT doesn't provide us a way to check completed dispatches.

All the templates for sending SMS and Bruin notes are in the folder `src/application/templates`, each vendor has its own folder and subfolder for sms templates.

### LIT Monitor

This section describe the way we monitor LIT dispatches.

Steps:

- Retrieve all dispatches
- Filter dispatches checking bruin notes to match only ours
- If the dispatch is not in redis, add to it
- Split filtered dispatches by status and run the processes concurrent
- Processes:
    * Confirmed monitor
        - Important fields to accomplish this task:
            - dispatch_number and ticket_id (`Dispatch_Number`, `MetTel_Bruin_TicketID`)
            - datetime and timezone of the dispatch (`Date_of_Dispatch`, `Hard_Time_of_Dispatch_Local`, `Hard_Time_of_Dispatch_Time_Zone_Local`)
            - tech_name (`Tech_First_Name`)
            - client phone (`Job_Site_Contact_Name_and_Phone_Number`)
            - tech phone (`Tech_Mobile_Number`)
        - Then we check all the notes from bruin to check what we already have
        - Perform the proper actions such, send sms or append notes or even check if the tech has change.
    * Tech on site monitor
        - Important fields to accomplish this task:
            - dispatch_number and ticket_id (`Dispatch_Number`, `MetTel_Bruin_TicketID`)
            - datetime and timezone of the dispatch (`Date_of_Dispatch`, `Hard_Time_of_Dispatch_Local`, `Hard_Time_of_Dispatch_Time_Zone_Local`)
            - client phone (`Job_Site_Contact_Name_and_Phone_Number`)
    * Canceled monitor
        - Important fields to accomplish this task:
            - dispatch_number and ticket_id (`Dispatch_Number`, `MetTel_Bruin_TicketID`)
            - datetime and timezone of the dispatch (`Date_of_Dispatch`, `Hard_Time_of_Dispatch_Local`, `Hard_Time_of_Dispatch_Time_Zone_Local`)

### CTS Monitor

This section describe the way we monitor CTS dispatches.

Steps:

- Retrieve all dispatches
- Processes:
    * Common to all processes:
        - dispatch_number and ticket_id (`Name`, `Ext_Ref_Num__c`)
        - igz_dispatch_number (`Description__c`, `IGZ Dispatch Number:`)
        - Filter dispatches checking bruin notes to match only ours
            * This step it is a bit tricky we need to send from the dispatch portal backend the uuid that we generated before and retrieve from the description field in CTS (`Description__c`)
        - If the dispatch is not in redis, add to it
        - process with depending on the current status
    * Confirmed monitor
        - Important fields to accomplish this task:
            - dispatch_number and ticket_id (`Name`, `Ext_Ref_Num__c`)
            - datetime of the dispatch in UTC (`Local_Site_Time__c`)
            - tech_name (`API_Resource_Name__c`)
            - dispatch status (`Status__c`)
            - client phone (`Description__c`, `Onsite Contact:`)
            - tech phone (`Description__c`, `Resource_Phone_Number__c`)
        - Then we check all the notes from bruin to check what we already have
        - Perform the proper actions such, send sms or append notes or even check if the tech has change.
    * Tech on site monitor
        - Important fields to accomplish this task:
            - dispatch_number and ticket_id (`Name`, `Ext_Ref_Num__c`)
            - datetime of the dispatch in UTC (`Local_Site_Time__c`)
            - dispatch status (`Status__c`)
            - client phone (`Description__c`, `Onsite Contact:`)
        - Then we check all the notes from bruin to check what we already have
        - Perform the proper actions such, send sms or append notes.
    * Canceled monitor
        - Important fields to accomplish this task:
            - dispatch_number and ticket_id (`Name`, `Ext_Ref_Num__c`)
            - datetime of the dispatch in UTC (`Local_Site_Time__c`)
            - dispatch status (`Status__c`)
            - client phone (`Description__c`, `Onsite Contact:`)
        - Then we check all the notes from bruin to check what we already have
        - Perform the proper actions such, send sms or append notes.


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

# Resources

- [SwaggerUI Quart](https://medium.com/@hkaraoguz/using-swaggerui-with-quart-72a3dab19273)
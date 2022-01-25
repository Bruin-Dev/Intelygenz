# Repair Tickets Monitor - Software Maintenance Guide (SMG)

## Repository

Link to the `automation-engine` repo: https://gitlab.intelygenz.com/mettel/automation-engine



## Development environment

To set up the virtual environment, first check that you have Docker and docker-compose installed.

If you do not have docker-compose, set it up with the following commands:

```shell
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

Make sure you have an env file (called `env` without a dot) containing the following env vars in the path `repair-tickets-monitor/src/config/`:

```text
ENVIRONMENT_NAME=
NATS_SERVER1=
REDIS_HOSTNAME=
REDIS_CACHE_HOSTNAME=
CURRENT_ENVIRONMENT=
PAPERTRAIL_ACTIVE=
PAPERTRAIL_HOST=
PAPERTRAIL_PORT=
```

In addition, the env files for other services need to exist, too. 
In order to generate them, use the `installation-utils/environment_files_generator.py` 
following the instructions in the README inside `automation-engine/installation-utils`. For the access token, ask a member of the Automation Team. 

Before continuing, make sure the following env variables are set:

- In `repair-tickets-monitor` (inside src/config/env):

```
ENVIRONMENT_NAME={name.surname}-local
NATS_SERVER1=nats://nats-server:4222
REDIS_HOSTNAME=redis
REDIS_EMAIL_TAGGER_HOSTNAME=redis-email-tagger
CURRENT_ENVIRONMENT=marc.vivancos-local
PAPERTRAIL_ACTIVE=False
PAPERTRAIL_HOST=logs.papertrailapp.com
PAPERTRAIL_PORT=1111
```

- In `repair-tickets-kre-bridge`  (inside src/config/env):

  ```
  ENVIRONMENT_NAME={name.surname}-local
  NATS_SERVER1=nats://nats-server:4222
  NATS_CLUSTER_NAME=automation-engine-nats
  REDIS_HOSTNAME=redis
  LAST_CONTACT_RECIPIENT=mettel@intelygenz.com
  CURRENT_ENVIRONMENT=dev
  PAPERTRAIL_ACTIVE=False
  PAPERTRAIL_HOST=logs.papertrailapp.com
  PAPERTRAIL_PORT=1111
  KRE_BASE_URL=host.docker.internal:9000
  ```

From the automation-engine directory, run docker-compose build:

```
> docker-compose build repair-tickets-monitor
```



If you encounter a problem with "basic auth credentials", first ensure you have AWS CLI, which you can install as follows:

```shell
# Install AWS locally
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS:
aws configure  # Opens interactive prompt. 
               
> Access Key:         # Ask Automation Team DevOps for access credentials
> Secret Access Key:  # Ask Automation Team DevOps for access credentials
> Default region name [None]: us-east-1
> Default output format [None]: json

# Login to AWS Elastic Container Registry
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 374050862540.dkr.ecr.us-east-1.amazonaws.com

# Proceed to docker-compose-build
```



## Interpreter 

If you can use the interpreter from inside the docker-compose (may require a Pro version of your IDE), do so. If not, create a virtual environment with pyenv -- more details to follow. (If you do not have pyenv in terminal, install it and add to path.) The Automation Engine uses Python 3.6. 

```
# To install Python 3.6:
pyenv install 3.6.13

## Add the new interpreter to IDE project settings
## Open new console with the venv activated

# Install libraries
pip install -r requirements
```



## Build docker compose

***Warning:** This creates a running environment of RTA Monitor, sending requests to Bruin and attempting to pass them to a KRE.*

```
# Make sure you are logged in to AWS ECR: 
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 374050862540.dkr.ecr.us-east-1.amazonaws.com

# Docker compose:
docker-compose up --build repair-tickets-monitor
```

To avoid attempting to send closed ticket feedback to KRE, comment the following line in `app.py`:

```python
# app.py, class Container 
    
    async def _start(self):
        await self._event_bus.connect()
        await self._new_created_tickets_feedback.start_created_ticket_feedback(exec_on_start=True)
        # await self._new_closed_tickets_feedback.start_closed_ticket_feedback(exec_on_start=True)
        await self._repair_tickets_monitor.start_repair_tickets_monitor(exec_on_start=True)
        self._scheduler.start()

```



## Installing KRE locally

Clone the KRE repo:

```
git clone git@github.com:konstellation-io/kre.git  
```

see official Konstellation README for instructions: https://www.konstellation.io/docs/kre/installation/local/





**TODO:**

- [ ] Documentation for installing a KRE instance of RTA locally (in progress)
- [ ] Doc for creating a Redis for testing purposes
- [ ] (In main RTA repo README) Doc for deploying a new version of KRT
- [ ] ...

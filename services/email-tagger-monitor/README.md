# Email tagger monitor
* [Description](#description)
* [Workflow](#workflow)
* [Capabilities used](#capabilities-used) 
* [Running in docker-compose](#running-in-docker-compose)

# Description
This service is responsible for tagging e-mails pushed by Bruin to an exposed REST API by using E-mail Tagger’s KRE, which returns the best suited tag for an e-mail based on the results of a predictive model.

# Workflow
__TODO__

# Capabilities used
- [Notifier](../notifier/README.md)
- [Email tagger KRE bridge](../email-tagger-kre-bridge/README.md)
- [Bruin bridge](../bruin-bridge/README.md)

![IMAGE: email-tagger-monitor_microservice_relationships](/docs/img/system_overview/use_cases/email-tagger-monitor_microservice_relationships.png)

# Running in docker-compose
- `docker-compose up --build nats-server redis redis-email-tagger`
- `docker-compose up --build bruin-bridge email-tagger-kre-bridge notifier`
- `docker-compose up --build email-tagger-monitor`

## Running with Bruin mock and Konstellation local 
You need a `bruin-mock-local` module and a file `docker-compose.local.yml` like this:

```yml
version: '3.6'
services:

  bruin-mock-local:
    build:
      # Context must be the root of the monorepo
      context: .
      dockerfile: bruin-mock-local/Dockerfile
      args:
        REPOSITORY_URL: 374050862540.dkr.ecr.us-east-1.amazonaws.com/automation
        DOCKER_BASE_IMAGE_VERSION: 2.2.0
    env_file:
      - bruin-mock-local/src/config/env
    ports:
      - 8066:8066
```

And you should edit `BRUIN_BASE_URL=http://bruin-mock-local:8066/` on `bruin-bridge/src/config/env` 

Find your local ip and edit and uncomment this code `docker-compose.yml`:
```yml
  email-tagger-kre-bridge:
    # NOTE: Extra hosts is needed only for local development with a KRE local
    #       Change to your host IP
    extra_hosts:
      - "host.docker.internal:192.168.1.134"
```

you should edit `grpc_secure_mode` to `False` on `email-tagger-kre-bridge/src/config/config.py`
```python
KRE_CONFIG = {
    'base_url': os.environ['KRE_BASE_URL'],
    # NOTE: Set to False for local development or manual tests
    'grpc_secure_mode': True
}
```

edit `KRE_BASE_URL=host.docker.internal:9000` en `email-tagger-kre-bridge/src/config/env`

the `REQUEST_SIGNATURE_SECRET_KEY=secret` should match with `email-tagger-monitor/scripts/local_notify_ticket.sh` secret field.

open a portforward on KST entrypoint pod to port 9000 and address 0.0.0.0 
- `docker-compose -f docker-compose.yml -f docker-compose.local.yml up --build bruin-bridge email-tagger-kre-bridge bruin-mock-local`
- `docker-compose up --build nats-server redis redis-email-tagger`
- `docker-compose up --build email-tagger-monitor`

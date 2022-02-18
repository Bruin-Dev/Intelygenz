# bruin-api-mock-local

The purpose of this service is to give the chance to test interactions between the [bruin-bridge](../bruin-bridge/README.md) and a simulated Bruin API in local environments.

The service is meant to reply with fixed payloads to requests arriving at endpoints, so those payloads can be modified at convenience to test the desired scenario.

# API 
There are two namespaces in this API:
1. `/login`: handles authentication against the simulated API.
2. `/api`: handles the access to common Bruin resources, such as tickets, details, notes, and so on.

# Up and running
There is a dependency set in the `docker-compose` file so that the `bruin-bridge` needs to wait for this service to be up & running before spinning up.

In case that you need to run it isolated, just run:
``
docker-compose up --build bruin-api-mock-local
```

Then we need make the `bruin-bridge` aim at this service by modifying the `bruin-bridge` `env` file this way:
```
BRUIN_LOGIN_URL=http://bruin-api-mock-local:15001/login
BRUIN_BASE_URL=http://bruin-api-mock-local:15001/api
```

That's all.
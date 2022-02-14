# bruin-api-mock-local

The propuse of this services is can tests in local the Bruin API without connecting to a real Bruin environment
What this expose is an replica of the original API service to feed the [bruin-bridge](../bruin-bridge/README.md).

# API 
There are two namespaces to API:
1. `/login`: That is the [login Bruin service](https://id.bruin.com/)
2. `/api`: That is the [API Bruin service](https://api.bruin.com/)

# Up and running
This is service is a depndency of bruin-bridge in docker-compose. but if you want to run isolated:
```
docker-compose up --build bruin-api-mock-local
```

Than we need to aim bruin-brindge to this service modifing the bruin-bridge env file on this way
```
BRUIN_LOGIN_URL=http://bruin-api-mock-local:15001/login
BRUIN_BASE_URL=http://bruin-api-mock-local:15001/api
```

That's all.
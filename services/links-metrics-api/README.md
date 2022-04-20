# Links metrics api
* [Description](#description)
* [Workflow](#workflow)
* [Capabilities used](#capabilities-used)
* [Running in docker-compose](#running-in-docker-compose)

# Description
This service is responsible for exposing a REST API that, upon receiving GET requests, makes it fetch a portion of the metrics time series collected by links-metrics-collector from the MongoDB instance.

# Workflow
__TODO__

# Capabilities used
This service is self-contained, i.e., it does not require access to NATS or Redis, or any other microservice within the Automation Engine. For that reason, it is not a REQuester or a REPlier.

![IMAGE: links-metrics-api_microservice_relationships](/docs/img/system_overview/isolated_services/links-metrics-api_microservice_relationships.png)

# Running in docker-compose
__TODO__


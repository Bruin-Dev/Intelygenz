# Ticket collector
* [Description](#description)
* [Workflow](#workflow)
* [Capabilities used](#capabilities-used)
* [Running in docker-compose](#running-in-docker-compose)

# Description
This service is responsible for collecting and storing information of Bruin tickets to a MongoDB instance.

# Workflow
__TODO__

# Capabilities used
Although the service clearly uses Bruin to fetch data, this service is self-contained, i.e., it does not require access to NATS or Redis, or any other microservice within the Automation Engine, which essentially means it does not use bruin-bridge.

![IMAGE: ticket-collector_microservice_relationships](/docs/img/system_overview/isolated_services/ticket-collector_microservice_relationships.png)

# Running in docker-compose
__TODO__
# Ticket statistics
* [Description](#description)
* [Workflow](#workflow)
* [Capabilities used](#capabilities-used)
* [Running in docker-compose](#running-in-docker-compose)

# Description
This service is responsible for:
- calculating ticket statistics based on the ticket data stored by ticket-collector, and store them to the MongoDB instance.
- exposing a REST API that, upon receiving GET requests, makes it fetch a subset of ticket statistics calculated by the periodic cycle from the MongoDB instance. These statistics are used to build some custom Grafana dashboards (these dashboards are not in the Automation’s Grafana instance, though).

# Workflow
__TODO__

# Capabilities used
This service is self-contained, i.e., it does not require access to NATS or Redis, or any other microservice within the Automation Engine.

![IMAGE: ticket-statistics_microservice_relationships](/docs/img/system_overview/isolated_services/ticket-statistics_microservice_relationships.png)

# Running in docker-compose
__TODO__

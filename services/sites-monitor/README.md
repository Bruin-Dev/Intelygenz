# Sites monitor
* [Description](#description)
* [Workflow](#workflow)
* [Velocloud integration](#velocloud-integration)
  * [Connecting to several clusters](#connecting-to-several-clusters)
  * [Service logic](#service-logic)
* [Capabilities used](#capabilities-used)
* [Running in docker-compose](#running-in-docker-compose)
 
# Description
This microservice requests data from the velocloud API via the velocloud-bridge microservice, using this information to enrich Prometheus. The prometheus data serves as a feed for Grafana.

# Work flow
__TODO__

# Velocloud integration
## Connecting to several clusters
Velocloud provided us with endpoints to make request calls to. The client that makes the request calls is located 
in the `client` folder of the `velocloud-bridge`.

The service's Velocloud client will create a client in a list for each host the service must connect to.

Credentials are put inside an environment variable with the next schema:
`some.host.name+hostusername+hostpassword;other.host.name+otherusername+otherpassword`

In the `config.py`script, there's a way to split this into an array of dictionaries like this one:
```python
config = {
    'url': "some.host.name",
    'username': "hostusername",
    'password': "hostpassword"
}
```

## Service logic
The service must ask for the list of edges of each host; each edge data will be paired with its enterprise and the host itself. Once it has collected
all the edges with it's enterprises, it must create a single task to process all edges.

The way to generate tasks is generate an event like this one
```python
event = {
    "host": "some.host.name",
    "id": 1,
    "enterpriseId": 19
}
```

Then the Sites Monitor will publish that task to the topic `edge.status.task`.

This action will be performed in cycles. The interval between them is defined in the env file (change this file affects 
environment configuration), in a snippet like this:
```
MONITORING_SECONDS=120
```

# Capabilities used
- [Notifier](../notifier/README.md)
- [Velocloud bridge](../velocloud-bridge/README.md)

![IMAGE: sites-monitor_microservice_relationships](/docs/img/system_overview/use_cases/sites-monitor_microservice_relationships.png)

# Running in docker-compose
First run: `docker-compose up --build velocloud-bridge grafana prometheus thanos-querier thanos-sidecar`
Wait until everything is up and running, and then run: `docker-compose up --build sites-monitor`

You can access to the metrics dashboards in localhost:3000 using the credentials in [here](../../metrics-dashboard/grafana/Dockerfile)

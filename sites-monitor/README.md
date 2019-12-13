# Table of contents
- [Velocloud integration](#velocloud-integration)
  * [Connecting to several clusters](#connecting-to-several-clusters)
  * [Service logic](#service-logic) 
  * [How to run it](#how-to-run-it) 

# Velocloud integration

## Connecting to several clusters
Velocloud provided us with endpoints to make request calls to. The client that makes the request calls is located 
in the `client` folder of the `velocloud-bridge`.

The service's Velocloud client will create a client in a list for each host the service must connect to.

Credentials are put inside an environment variable with the next schema:
`some.host.name+hostusername+hostpassword;other.host.name+otherusername+otherpassword`

In the `config.py`script, there's a way to split this into an array of dictionaries like this one:

````
        {'url': "some.host.name",
         'username': "hostusername",
         'password': "hostpassword"
         }
````

## Service logic
The service must ask for the list of edges of each host; each edge data will be paired with its enterprise and the host itself. Once it has collected
all the edges with it's enterprises, it must create a single task for each one.

The way to generate tasks is generate an event like this one

````
{
    "host": "some.host.name",
    "id": 1,
    "enterpriseId": 19
}
````

Then the Sites Monitor will publish that task to the topic `edge.status.task`.

This action will be performed in cycles. The interval between them is defined in the config file, in a snippet like this:

````
SITES_MONITOR_CONFIG = {
    'interval_time': 600
}
````
## How to run it
````$
docker-compose up --build nats-server velocloud-bridge prometheus grafana 
# Wait until everything is up and running
docker-compose up --build sites-monitor
````

You can access to the metrics dashboards in localhost:3000 using the credentials in [here](../metrics-dashboard/grafana/Dockerfile)
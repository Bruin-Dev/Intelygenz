# Table of contents
- [Velocloud SDK integration](#velocloud-sdk-integration)
  * [Connecting to several clusters](#connecting-to-several-clusters)
  * [Velocloud logic](#velocloud-logic) 

# Velocloud SDK integration

## Connecting to several clusters
Velocloud provided us with an SDK. The SDK is currently located in the `custompackages` folder, so we use a locked
and customized (for large amounts of requests) version of it.

The service's Velocloud client will create a Velocloud's SDK client for each cluster the service must connect to.

Credentials are put inside an enviroment variable with the next schema:
`some.host.name+hostusername+hostpassword;other.host.name+otherusername+otherpassword`

In the `config.py`script, there's a way to split this into an array of dictionaries like this one:

````
        {'url': "some.host.name",
         'username': "hostusername",
         'password': "hostpassword"
         }
````

## Velocloud logic
The service must ask, for each cluster, for a list of each edge, paired with it's enterprise. Once it has collected
all the edges with it's enterprises, it must create a single task for each one.

The way to generate tasks is generate an event like this one

````
{
    "host": "some.host.name",
    "id": 1,
    "enterpriseId": 19
}
````

Then the Overseer will publish that task to the topic `edge.status.task`.

This action will be performed in cycles. The interval between them is defined in the config file, in a snippet like this:

````
OVERSEER_CONFIG = {
    'interval_time': 600
}
````

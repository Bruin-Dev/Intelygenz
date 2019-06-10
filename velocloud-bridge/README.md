# Table of contents
- [Velocloud SDK integration](#velocloud-sdk-integration)
  * [Connecting to several clusters](#connecting-to-several-clusters)
  * [Service logic](#service-logic)
  * [Parallel bridges](#parallel-bridges)

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

## Service logic
The bridge will subscribe to both `edge.list.request` and `edge.status.request`.

When a message is received from `edge.list.request` the bridge will call upon velocloud and publish a 
a list of edge ids to `edge.list.response`, formed as it is shown in the next schema:. 

__edge.list.request schema__
```
{
 "request_id": "c681c72a-9c52-4c74-bd99-53c2c973b037"(per-request generated UUID),
 "filter": [{"host": "some.host", "enterprise_ids": [19,42,99] }](leave blank for all hosts and enterprises)
}
```
__edge.list.response schema__
```
{
 "request_id": "c681c72a-9c52-4c74-bd99-53c2c973b037",
 "edges": [{"host": "some.host", "enterprise_id":19, "edge_id":99}],
 "status": 200 
}
```

If a filter is given in the `edge.list.request` message then only the edges in the filter will be published.
The filter uses a list comprehension that only grabs edge info that matches the host info and enterprise id given in the
filter. If no enterprise id is given in the filter then every edge in that host will be published.

When a message is received from `edge.status.request` the bridge will get the specific edge status and link status and
send to `edge.status.response`

__edge.status.request schema__
```
 {
 "request_id": "4a1c306f-fdca-4e84-bdd0-363e88e76d2a",
 "edge": {"host": "some.host", "enterprise_id":19, "edge_id":99}
 }
```
__edge.status.request schema__
```
{
 "request_id": "4a1c306f-fdca-4e84-bdd0-363e88e76d2a",
 "edge_info": {....},
 "status": 200
}
```

## Parallel bridges
Is possible to have more than one replica of the bridge working. They are in the same `durable group`(durable_name + queue in code) in NATS, so they share
the same offset as long as they belong to the same `durable group`.

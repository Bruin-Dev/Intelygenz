# Table of contents
- [Velocloud integration](#velocloud-integration)
  * [Connecting to several clusters](#connecting-to-several-clusters)
  * [Service logic](#service-logic)

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
The bridge will subscribe to `edge.list.request`, `edge.status.request`, and `alert.request.event.edge`.

When a message is received from `edge.list.request` the bridge will call upon velocloud and publish a 
list of edge ids to a response topic that was built by NATS under the hood:

__edge.list.request schema__
```
{
 "request_id": "c681c72a-9c52-4c74-bd99-53c2c973b037" (per-request generated UUID),
 "body":{
    "filter": [{"host": "some.host", "enterprise_ids": [19,42,99] }](leave blank for all hosts and enterprises)
 }
}
```
__edge.list.response.{some service id} schema__
```
{
 "request_id": "c681c72a-9c52-4c74-bd99-53c2c973b037",
 "body": [{"host": "some.host", "enterprise_id":19, "edge_id":99}],
 "status": 200 
}
```

If a filter is given in the `edge.list.request` message then only the edges in the filter will be published.
The filter uses a list comprehension that only grabs edge info that matches the host info and enterprise id given in the
filter. If no enterprise id is given in the filter then every edge in that host will be published.

When a message is received from `edge.status.request` the bridge will get the specific edge status and link status and
send to to a response topic that was built by NATS under the hood:

__edge.status.request schema__
```
 {
 "request_id": "4a1c306f-fdca-4e84-bdd0-363e88e76d2a",
 "body": {"host": "some.host", "enterprise_id":19, "edge_id":99}
 }
```
__edge.status.response.{some service id} schema__
```
{
 "request_id": "4a1c306f-fdca-4e84-bdd0-363e88e76d2a",
 "body":{
    "edge_id":{"host": "some.host", "enterprise_id":19, "edge_id":99},
     "edge_info": {....},
 }
 "status": 200
}
```

When a message is received by `alert.request.event.edge`, the bridge will get the specific edge event and send to
a response topic that was built by NATS under the hood:

__alert.request.event.edge schema__
```
{
    'request_id': 123,
    'body':{
        'edge': {"host": "some.host", "enterprise_id":19, "edge_id":99},
        'start_date': '2019-07-19 14:19:45',  # Seven days before end_date
        'end_date': '2019-07-26 14:19:45',
        'filter': ['EDGE_UP']
        'limit':  200
    }
}
```
The `filter` field is used to request from the bridge only events that have event names in the list. If no filter is provided
all events are returned.

The `limit` field is used to limit how many events do we actually want to be returned. If no limit is provided then 
all events are returned.

__alert.response.event.edge.{some service id} schema__
```
{
    'request_id': 123, 
    'body': {...}, 
    'status': 200
}
```

When a message is received by `edge.ids.by.serial`, the bridge will get the edge_id that corresponds to the given 
serial number and send to a response topic that was built by NATS under the hood:
__edge.ids.by.serial schema__
```
{
    "request_id": 123, 
    "serial": "VCO4"
}
```
Velocloud-bridge will create a dictionary of serials to edge_ids and store it into redis. This dictionary gets 
reset and made every day. The `serial` provided in the message is used to search to see if that key exists in
the dictionary and then the corresponding edge_id will be returned. 

__edge.ids.by.serial response schema__
```
{
    "request_id": 123, 
    "edge_id": [{"host": "some.host", "enterprise_id":19, "edge_id":99}], 
    "status": 200
}
```
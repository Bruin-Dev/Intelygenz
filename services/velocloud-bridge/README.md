# Velocloud bridge
* [Description](#description)
* [Connecting to several clusters](#connecting-to-several-clusters)
* [Requests](#requests)
  * [Alert request event edge](#alert-request-event-edge)
  * [Alert request event enterprise](#alert-request-event-enterprise)
  * [Get links with edge info](#get-links-with-edge-info)
  * [Get links metric info](#get-links-metric-info)
  * [Request enterprises names](#request-enterprises-names)

# Description
This microservice is in charge of making requests to the velocloud API, taking the role of replier in the context of NATS.

When another microservice requests velocloud data, it will be in charge of making response messages to the same and never of request, that is to say, it will always be a producer within a NATS topic and never a consumer.

![IMAGE: velocloud-bridge_microservice_relationships](/docs/img/system_overview/capabilities/velocloud-bridge_microservice_relationships.png)

# Connecting to several clusters
Velocloud provided us with endpoints to make request calls to. The client that makes the request calls is located 
in the `client` folder of the `velocloud-bridge`.

The service's Velocloud client will create a client in a list for each host the service must connect to.

Credentials are put inside an environment variable with the next schema:
`some.host.name+hostusername+hostpassword;other.host.name+otherusername+otherpassword`

In the `config.py`script, there's a way to split this into an array of dictionaries like this one:
```
        {'url': "some.host.name",
         'username': "hostusername",
         'password': "hostpassword"
         }
```

# Requests
## Alert request event edge
When a message is received by `alert.request.event.edge`, the bridge will get the
specific edge event and send to a response topic that was built by NATS under the hood:

The `filter` field is used to request from the bridge only events that have event names in the list. If no filter is provided
all events are returned.

The `limit` field is used to limit how many events do we actually want to be returned. If no limit is provided then
all events are returned.

```python
request_message = {
    'request_id': 123,
    'body': {
        'edge': {
            "host": "some.host", 
            "enterprise_id": 19, 
            "edge_id": 99,
        },
        'start_date': '2019-07-19 14:19:45',  # Seven days before end_date
        'end_date': '2019-07-26 14:19:45',
        'filter': ['EDGE_UP'],
        'limit':  200,
    },
}

# __alert.response.event.edge.{some service id}__
response_message = {
    'request_id': request_message['request_id'], 
    'body': {}, # body content
    'status': 200
}
```

## Alert request event enterprise
When a message is received by `alert.request.event.enterprise`, the bridge will get the 
specific enterprise events and send to a response topic that was built by NATS under the hood:

```
request_message = {
    'request_id': 123,
    'body':{
        'host': "some.host", 
        'enterprise_id':19, 
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

### Response message
__alert.response.event.enterprise.{some service id} schema__
```
{
    'request_id': 123, 
    'body': {...}, 
    'status': 200
}
```

## Get links with edge info
When `get.links.with.edge.info` receives the `host` parameter it will return all the links corresponding to the host 

### Request message
```
{
    "request_id": 123, 
    "body": {"host": "some.host"}
}
```

### Response message
```
{
    "request_id": 123, 
    "body": [{"enterpriseName":"Example - enterprise",
                "enterpriseId":1234,
                "enterpriseProxyId":null,
                "enterpriseProxyName":null,
                "edgeName":"Example | Node_520_example",
                "edgeState": "OFFLINE",
                "edgeSystemUpSince":"2020-01-21T23:05:28.000Z",
                "edgeServiceUpSince":"2020-01-21T23:06:21.000Z",
                "edgeLastContact":"2020-01-21T23:07:19.000Z",
                "edgeId":140,
                "edgeSerialNumber":"VC05200054422",
                "edgeHASerialNumber":null,
                "edgeModelNumber":"edge520",
                "edgeLatitude":42.988998,
                "edgeLongitude":-88.117996,
                "displayName":null,
                "isp":null,"interface":null,
                "internalId":null,
                "linkState":null,
                "linkLastActive":null,
                "linkVpnState":null,
                "linkId":null,
                "linkIpAddress":null,
                "host":"metvco04.mettel.net"}], 
    "status": 200
}
```

## Get links metric info
When get.links.metric.info receives the host and interval parameter it will return the information of all links in this 
interval for this host

### Request message
```
{
    "request_id": 123, 
    "body": {
                "host": "some.host",
                "interval": {
                                'start': '2020-10-19T15:22:03.345Z',
                                'end': '2020-10-19T16:22:03.345Z',
                            }
            }
}
```

### Response message
```
{
    "request_id": 123, 
    "body": [
                {
                    "linkId":22,
                    "bytesTx":9315705,
                    "bytesRx":20144885,
                    "packetsTx":87296,
                    "packetsRx":95621,
                    "totalBytes":29460590,
                    "totalPackets":182917,
                    "p1BytesRx":11204898,
                    "p1BytesTx":224105,
                    "p1PacketsRx":20789,
                    "p1PacketsTx":1237,
                    "p2BytesRx":4632130,
                    "p2BytesTx":2910548,
                    "p2PacketsRx":6321,
                    "p2PacketsTx":12358,
                    "p3BytesRx":153343,
                    "p3BytesTx":91914,
                    "p3PacketsRx":303,
                    "p3PacketsTx":368,
                    "controlBytesRx":4154514,
                    "controlBytesTx":6089138,
                    "controlPacketsRx":68208,
                    "controlPacketsTx":73333,
                    "bpsOfBestPathRx":134893000,
                    "bpsOfBestPathTx":43194000,
                    "bestJitterMsRx":0,
                    "bestJitterMsTx":0.0833,
                    "bestLatencyMsRx":2,
                    "bestLatencyMsTx":5.9167,
                    "bestLossPctRx":0,
                    "bestLossPctTx":0,
                    "scoreTx":4.400000095367432,
                    "scoreRx":4.400000095367432,
                    "signalStrength":0,
                    "state":0,
                    "name":"GE1",
                    "link":{
                                "enterpriseName":"FIS - EID12378_CID0152_BBT|87957|",
                                "enterpriseId":4,
                                "enterpriseProxyId":null,
                                "enterpriseProxyName":null,
                                "edgeName":"FIS | EID12378_CID0152_BBT_MAIN_540HA ",
                                "edgeState":"CONNECTED",
                                "edgeSystemUpSince":"2020-08-11T22:13:42.000Z",
                                "edgeServiceUpSince":"2020-09-23T07:40:48.000Z",
                                "edgeLastContact":"2020-11-03T13:28:22.000Z",
                                "edgeId":10,
                                "edgeSerialNumber":"VC05400017918",
                                "edgeHASerialNumber":"VC05400018557",
                                "edgeModelNumber":"edge540",
                                "edgeLatitude":41.938,
                                "edgeLongitude":-87.833,
                                "displayName":"173.167.163.179",
                                "isp":null,
                                "interface":"GE1",
                                "internalId":"00000001-d68c-4afd-a5db-0ca967b7209d",
                                "linkState":"STABLE",
                                "linkLastActive":"2020-11-03T13:25:02.000Z",
                                "linkVpnState":"STABLE",
                                "linkId":22,
                                "linkIpAddress":"173.167.163.179",
                                "host":"metvco04.mettel.net"
                    }
            ], 
    "status": 200
}
```

## Request enterprises names
When request.enterprises.names receives the filter is empty list returns all enterprise names. If you send some value in 
this list return the name of enterprises that have the same name.

### Request message
```
{
    "request_id": 123, 
    "body": {
                "filter": []
            }
}
```

### Response message
```
{
    "request_id": 123, 
    "body": ["enterprise_name_1", "enterprise_name_2", "enterprise_name_3", "enterprise_name_4"], 
    "status": 200
}
```

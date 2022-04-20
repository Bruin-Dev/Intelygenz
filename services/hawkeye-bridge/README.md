# Hawkeye bridge
* [Description](#description)
* [Links](#links)
* [Requests](#requests)
  * [Get probes](#get-probes)
  * [Get test results](#get-test-results)
* [Running in docker-compose](#running-in-docker-compose)

# Description
Hawkeye Bridge is used to make calls to the Hawkeye API.

![IMAGE: hawkeye-bridge_microservice_relationships](/docs/img/system_overview/capabilities/hawkeye-bridge_microservice_relationships.png)

# Links
- Hawkeye app: https://ixia.metconnect.net/ixrr_login.php
- Hawkeye swagger: https://ixia.metconnect.net/swagger/index.html

# Requests
## Get probes
When the hawkeye bridge receives a request with a request message from topic `hawkeye.probe.request` it makes a callback
to function `get_probe`. This request can have the `status` or `serial_number` parameters to filter the results of the
call

```python
request_message = {
    "request_id": "1234",
    "body": {
        "status": "down",
    },
}

response_message = {
    "request_id": request_message["request_id"],
    "body": [
        {
            "probeId": "27",
            "uid": "b8:27:eb:76:a8:de",
            "os": "Linux ARM",
            "name": "FIS_Demo_XrPi",
            "testIp": "none",
            "managementIp": "none",
            "active": "1",
            "type": "8",
            "mode": "Automatic",
            "n2nMode": "1",
            "rsMode": "1",
            "typeName": "xr_pi",
            "serialNumber": "B827EB76A8DE",
            "probeGroup": "FIS",
            "location": "",
            "latitude": "0",
            "longitude": "0",
            "endpointVersion": "9.6 SP1 build 121",
            "xrVersion": "4.2.2.10681008",
            "defaultInterface": "eth0",
            "defaultGateway": "192.168.90.99",
            "availableForMesh": "1",
            "lastRestart": "2020-10-15T02:13:24Z",
            "availability": {
                "from": 1,
                "to": 1,
                "mesh": "1",
            },
            "ips": [
                "192.168.90.102",
                "192.226.111.211",
            ],
            "userGroups": [
                "1",
                "10",
            ],
            "wifi": {
                "available": 0,
                "associated": 0,
                "bssid": "",
                "ssid": "",
                "frequency": "",
                "level": "0",
                "bitrate": "",
            },
            "nodetonode": {
                "status": 0,
                "lastUpdate": "2020-11-06T10:38:07Z",
            },
            "realservice": {
                "status": 0,
                "lastUpdate": "2020-10-15T02:18:28Z",
            },
        },
    ],
    "status": 200,
}
```

## Get test results
When the hawkeye bridge receives a request with a request message from topic `hawkeye.test.request` it makes a callback
to function `get_test_results`. This request must have keys `probe_uids` and one dictionary called `interval`, which
has `start` and `end` parameters to filter the results of the call

```python
request_message = {
    "request_id": "1234",
    "body": {
        "probe_uids": [
            "ATL_XR2000_1"
        ], 
        "interval":{
            "start": "2021-01-25 12:14:39.603347",
            "end": "2021-01-25 12:00:49.998494",
        } ,
    },
}

response_message = {
    "request_id": request_message["request_id"],
    "body": {
        "ATL_XR2000_1": {
            "summary": {
                "id": "DlfsJHcB0dCO9W0n6nGC",
                "date": "2021-01-21T15:21:55Z",
                "duration": 0,
                "meshId": 0,
                "mesh": 0,
                "module": "RealService",
                "probeFrom": "ATL_XR2000_1",
                "probeTo": "8.8.8.8",
                "reasonCause": "",
                "status": "Passed",
                "testId": "316",
                "testOptions": "Destination Servers: 8.8.8.8 Interval: 20 ms Count: 100 packets Packet Size:"
                               " 32 bytes (74) IP Protocol: ipv4 Class of Service: Best Effort Jitter "
                               "Calculation: Enabled",
                "testTag": "Core",
                "testType": "ICMP Test",
                "userId": "1"
            },  
            "metrics": [
                {
                    "metric": "Datagrams Out of Order",
                    "pairName": "Voice from->to",
                    "value": "0",
                    "threshold": "1",
                    "thresholdType": "0",
                    "status": "Passed"
                },
                {
                    "metric": "Delay (ms)",
                    "pairName": "Voice from->to",
                    "value": "1",
                    "threshold": "100",
                    "thresholdType": "0",
                    "status": "Passed"
                },
                {
                    "metric": "Jitter (ms)",
                    "pairName": "Voice from->to",
                    "value": "0.03",
                    "threshold": "5",
                    "thresholdType": "0",
                    "status": "Passed"
                },
            ],
        },
    }, 
    "status": 200,
}
```

# Running in docker-compose
`docker-compose up --build redis nats-server hawkeye-bridge`

# Table of contents
- [Hawkeye API](#hawkeye-api)
  - [Description](#description)
  - [Links](#links)
- [Running in docker-compose](#running-in-docker-compose)

# Hawkeye API

## Description
Hawkeye Bridge is used to make calls to the Hawkeye API.

# Get probes
### Description
When the hawkeye bridge receives a request with a request message from topic `hawkeye.probe.request` it makes a callback
to function `get_probe`. This request can have the `status` or `serial_number` parameters to filter the results of the call

### Request message
```
{
  "request_id": "1234",
  "body": {
    "status": "down"
  }
}
```
### Response message
```
{
  "request_id": "1234",
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
        "mesh": "1"
      },
      "ips": [
        "192.168.90.102",
        "192.226.111.211"
      ],
      "userGroups": [
        "1",
        "10"
      ],
      "wifi": {
        "available": 0,
        "associated": 0,
        "bssid": "",
        "ssid": "",
        "frequency": "",
        "level": "0",
        "bitrate": ""
      },
      "nodetonode": {
        "status": 0,
        "lastUpdate": "2020-11-06T10:38:07Z"
      },
      "realservice": {
        "status": 0,
        "lastUpdate": "2020-10-15T02:18:28Z"
      }
    }
  ],
  "status": 200
}
```

## Links
Hawkeye swagger:
https://ixia.metconnect.net/swagger/index.html

Hawkeye app:
https://ixia.metconnect.net/ixrr_login.php

# Running in docker-compose 
`docker-compose up --build redis nats-server hawkeye-bridge`
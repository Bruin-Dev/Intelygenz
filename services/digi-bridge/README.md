## DiGi bridge
* [Description](#description)
* [Requests](#requests)
   * [DiGi reboot](#digi-reboot) 
   * [Get DiGi recovery logs](#get-digi-recovery-logs) 
* [Entrypoint note](#entrypoint-note)
* [Running in docker-compose](#running-in-docker-compose)

## Description
The DiGi bridge is used to call the DiGi API to reboot DiGi links.

![IMAGE: digi-bridge_microservice_relationships](/docs/img/system_overview/capabilities/digi-bridge_microservice_relationships.png)

# Requests
## DiGi reboot
When the digi-bridge receives a request message from topic `digi.reboot` it makes a callback to the function `digi_reboot` 
to call the DiGi API to reboot the given DiGi link. The required fields needed are `velo_serial`,  `ticket`, and
`MAC`.

```python
request_message = {
    "request_id": "kNxC7FxXpg5ApdgGaX7otC",  ## UUID
    "body": {
        "velo_serial": "VC05400002265",  
        "ticket": 321,  
        "MAC": "00:04:2D:123",
    },
}

response_message = {
    "request_id": request_message["request_id"], 
    "body": [
        {
            "Message": "DiGi Device Recovery started, check Bruin ticket 5200960 later for details.. Process ID = 9847446", 
            "VeloSerial": "VC05200038370", 
            "SiteName": "KA02316VC", 
            "VeloInterface": {
                "Interface": "GE2",
            }, 
            "DiscoveredIP": {
                "IPAddress": "10.1.3.4",
            }, 
            "Carrier": {
                "Carrier": "VZW",
            }, 
            "DiscoveredMAC": {
                "MAC": "00042d09c44b",
            }, 
            "Ticket": "5200960",
        },
    ],
    "status": 200,
}
```

## Get DiGi recovery logs
When the digi-bridge receives a request message from topic `get.digi.recovery.logs` it makes a callback to the function `get_digi_recovery_logs` 
to call the DiGi API to get the DiGi recovery logs. All the fields are optional, and those fields are `igzID`,  `start_date_time`, 
`size`, and `offset`.

```python
request_message = {
    "request_id": "kNxC7FxXpg5ApdgGaX7otC",  ## UUID
    "body": {
        "igzID": "42",  ## Optional
        "start_date_time": "2021-02-15T16:08:26Z",  ## Optional
        "size": "10", ## Optional
        "offset": "0", ## Optional
    },
}

response_message = {
    "request_id": request_message["request_id"], 
    "body": {
        "Logs": [
            {
                "Id": 142,
                "igzID": "42",
                "RequestID": "959b1e34-2b10-4e04-967e-7ac268d2cb1b",
                "Method": "API Start",
                "System": "NYD",
                "VeloSerial": "VC00000613",
                "TicketID": "3569284",
                "DeviceSN": "NYD",
                "Notes": "Notes",
                "TimestampSTART": "2021-02-15T16:08:26Z",
                "TimestampEND": "2021-02-15T16:08:28Z",
            },
        ],
        "Count": 10,
        "Size": "50",
        "Offset": "0",
   },
   "status": 200,
}
```

# Entrypoint note
Since Mettel won't expose their DNS server, we need to modify the /etc/hosts file to contain the domain name translation.
That's why, instead of executing app.py as the rest of the services, this service has a `entrypoint.sh`
script which first will modify the /etc/hosts file and then will launch with python the `app.py` file.

# Running in docker-compose 
`docker-compose up --build redis nats-server digi-bridge`

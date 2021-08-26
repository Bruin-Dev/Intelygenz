# Table of contents
  * [Description](#description)
  * [Work Flow](#work-flow)
  * [Behaviour in dev and in pro](#behaviour-in-development-and-in-production)
  * [Capabilities used](#capabilities-used) 
  * [Running in docker-compose](#running-in-docker-compose)

# Description
The service affecting monitor is currently used to monitor a subset of edges (located at `config/contact_info.py`)
in order to detect if its latency, packet loss or jitter utilization exceeds a given threshold.

If it does, then a ticket is created or reopened, in case it exists and it"s resolved.

> Bear in mind that the whole affecting monitoring process runs every 10 minutes.

# Work Flow
This is the algorithm implemented to carry out the monitoring of edges:

1. Get the cache of customers for the Velocloud host(s) specified in `config/contact_info.py
2. Run three different processes, one for each kind of trouble: latency, packet loss, jitter and bandwidth over utilization.
3. Get the metrics collected during the last `10 minutes` for all links in the Velocloud host(s) specified in `config/contact_info.py
4. Filter links metrics to get metrics of those links under edges that exist in the cache of customers and also in `config/contact_info.py`
5. Map link metrics with contact info (extracted from `config/contact_info.py`) and Bruin customer info (extracted from customer cache).
 
   This mapping leads to a structure very similar to this (may contain more fields, but they are not used throughout the process):
   ```json
    [
        {
            "edge_status": {
                "host": "mettel.velocloud.net",
                "enterpriseId": 12345,
                "edgeId": 67890,
                "edgeName": "TEST",
                "edgeState": "OFFLINE",
                "edgeSerialNumber": "VC1234567",
                "enterprise_name": "Mettel|9994|"
            },
            "link_status": {
                "interface": "GE1",
                "displayName": "Test"
            },
            "link_metrics": {
                "bestLatencyMsRx": 121,
                "bestLatencyMsTx": 119,
                "bestLossPctRx": 9,
                "bestLossPctTx": 7,
                "bestJitterMsRx": 31,
                "bestJitterMsTx": 29,
                "bytesRx": 100,
                "bytesTx": 100,
                "bpsOfBestPathRx": 10,
                "bpsOfBestPathTx": 10
            },
            "cached_info": {
                "edge": {
                    "host": "mettel.velocloud.net",
                    "enterprise_id": 12345,
                    "edge_id": 67890
                },
                "bruin_client_info": {
                    "client_id": 9994,
                    "client_name": "METTEL/NEW YORK"
                },
                "serial_number": "VC1234567"
            },
            "contact_info": {
                "ticket": {
                    "email": "fake@gmail.com",
                    "phone": "111-111-1111",
                    "name": "Fake Guy"
                },
                "site": {
                    "email": "fake@gmail.com",
                    "phone": "111-111-1111",
                    "name": "Fake Guy"
                }
            }
        }
    ]
   ```

6. For every link in the mapping above:
   1. Check if any of the metrics exceeds the thresholds defined for the trouble check (latency, packet loss or jitter)
      1. If so, and if the current environment is `PRODUCTION`:
         1. Look for an affecting ticket associated to the serial number of the edge this link belongs to
            1. If there is no affecting ticket, create a new one and append a note with the details of the trouble found
            2. If there is a ticket and it's resolved, unresolve it
            3. Otherwise, don't take any further action
      2. Otherwise, don't take any further action

## Thesholds
### Latency
A link can have a latency of up to `120 milliseconds` when transmitting or receiving info. If this threshold is
exceeded, the process will report this issue.

### Packet loss
A link can lose up to `8 packets` when transmitting or receiving info. If this threshold is
exceeded, the process will report this issue.

### Jitter
A link can stay in jitter state up to `30 milliseconds` when transmitting or receiving info. If this threshold is
exceeded, the process will report this issue.

### Bandwidth Over Utilization
A link can use up to `80%` of the available bandwidth when transmitting or receiving info. If this threshold is
exceeded, the process will report this issue. 

# Capabilities used
- [Customer cache](../customer-cache/README.md)
- [Velocloud bridge](../velocloud-bridge/README.md)
- [Bruin bridge](../bruin-bridge/README.md)
- [Notifier](../notifier/README.md)

# Running in docker-compose
`docker-compose up --build redis nats-server velocloud-bridge notifier customer-cache service-affecting-monitor`

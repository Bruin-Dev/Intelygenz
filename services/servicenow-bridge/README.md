# Table of contents
  * [ServiceNow API](#servicenow-api)
    * [Description](#description)
  * [Report Incident](#report-incident)
    * [Description](#description-1)
    * [Request message](#request-message-1)
    * [Response message](#response-message-1)
  * [Running in docker-compose](#running-in-docker-compose)

# ServiceNow API
### Description

The `servicenow-bridge` is used to call to the ServiceNow API.

# Report Incident
### Description
When the `servicenow-bridge` receives a request with a request message from topic `servicenow.incident.report.request` it calls the `report_incident` function.
The request message contains all of the fields needed to report an incident. These fields are `host`, `gateway`, `summary` and `note`. 
Once all of the fields are extracted from the request message, a call to the `servicenow_repository` is made.
We then format the API response into a response message and publish it to the response topic that was built by NATS under the hood.

### Request message
```
{
    "request_id": uuid(),
    "body": {
        "host": "mettel.velocloud.net",
        "gateway": "vcg-test-1",
        "summary": "Incident summary",
        "note": "Incident note"
    }
}
```

### Response message
```
{
    'request_id': msg_dict['request_id'],
    'body': Result received from the servicenow_client,
    'status': 201
}
```

# Running in docker-compose 
`docker-compose up --build redis nats-server servicenow-bridge`

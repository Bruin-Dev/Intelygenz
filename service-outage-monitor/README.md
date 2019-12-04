# Table of contents
  * [Description](#description)
  * [Work Flow](#work-flow)
  * [Capabilities used](#capabilities-used) 
  * [Running in docker-compose](#running-in-docker-compose)

# Description
The objective of `service-outage-monitor` is to detect faulty edges which are not linked in any way to an open
Bruin ticket and send a report with all those edges via e-mail. Note that edges targeted at testing purposes are not included.

> At this moment, this microservice is disabled in production environment because edges in `decomissioned` and
`maintenance` state should not be monitored.

This report is sent **every hour** and contains the list of faulty edges represented as a table like:

| Date of detection | Serial Number |   Company   |                                     Edge URL                                 |   Outage causes  |
|:-----------------:|:-------------:|:-----------:|:----------------------------------------------------------------------------:|:----------------:|
|     <detection_date_1>    |   <serial_number_1>  | <company_1> | <edge_url_1> | <outage_causes_list_1> |
|     <detection_date_2>    |   <serial_number_2>  | <company_2> | <edge_url_2> | <outage_causes_list_2> |
|     <detection_date_N>    |   <serial_number_N>  | <company_N> | <edge_url_N> | <outage_causes_list_N> |

where:
- **Date of detection**. Points out when the outage in an edge was first detected. It's a datetime represented with format `YYYY-MM-DD HH:mm:ss`.
- **Serial number**. The serial number of the faulty edge.
- **Company**. The company this edge belongs to.
- **Edge URL**. The URL of this edge in the Velocloud system.
- **Outage causes**. The reasons why the edge became faulty. It's a list containing a network element (either a link or the edge itself) and
  the state that caused the outage (as of now, this state is `OFFLINE` for edges and `DISCONNECTED` for links).

Besides this table, the e-mail has a CSV file like the following one attached to it:
```
detection_time,enterprise,links,serial_number,outage_causes
<detection_date_1>,<company_1>,<edge_url_1>,<serial_number_1>,<comma_separated_causes_1>
<detection_date_2>,<company_2>,<edge_url_2>,<serial_number_2>,<comma_separated_causes_2>
<detection_date_N>,<company_N>,<edge_url_N>,<serial_number_N>,<comma_separated_causes_N>
```

# Work Flow

### Considerations
The outage report process is divided into three APScheduler jobs that communicate through a Redis instance. Bear in mind these two
terms to understand the role of every job:
- **Quarantine**. The quarantine is a subset of Redis keys that start with the prefix `EDGES_QUARANTINE`.
- **Reporting queue**. The reporting queue is a subset of Redis keys that start with the prefix `EDGES_TO_REPORT`.

## Outage detector job
This job runs **every 40 minutes** and is in charge of claiming the status of all the edges from the Velocloud API that belong to
the enterprises under monitoring.
- If an edge is in `DISCONNECTED` state or any of its links is `OFFLINE`, its status is put into quarantine.
- If that is not the case, then the edge is just ignored as there is no interest in healthy edges for this report.

## Quarantine job
This one runs **every 10 minutes**. Its duty is to pull all the edges statuses from the Redis quarantine
and check if they are still in an outage state.
- If the edge from quarantine is still in an outage condition and there is no outage ticket open in the Bruin service, then the edge
  is moved from quarantine to the reporting queue.
- Otherwise, no action is applied to this edge. It is just kept into quarantine for the next quarantine job.

> In case of a crash of the `service-outage-monitor` microservice, there is a mechanism implemented that triggers one
job per edge stored in quarantine as soon as the microservice is restarted. This way the quarantine is processed before
pulling edges statuses from the Velocloud API.

## Reporter job
This job is executed **every hour** and it simply:
- Builds an HTML-formatted text containing a table with all the edges stored in the reporting queue,
- Embeds the text (along with a CSV containing all the info of the faulty edges) into an e-mail, and
- Sends it to the proper recipients.

After that sequence of steps, the reporting queue is cleared up so it does not pollute subsequent reports.

> In case of a crash of the `service-outage-monitor` microservice, edges stored in the reporting queue are sent via e-mail as soon
as the microservice restarts.

# Capabilities used
- [Velocloud bridge](../velocloud-bridge/README.md)
- [Bruin bridge](../bruin-bridge/README.md)
- [Notifier](../notifier/README.md)

# Running in docker-compose
`docker-compose up --build redis velocloud-bridge bruin-bridge notifier nats-server service-outage-monitor`

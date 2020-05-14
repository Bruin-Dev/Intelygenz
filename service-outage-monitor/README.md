# Table of contents
  * [Description](#description)
  * [Outage monitoring](#outage-monitoring)
  * [Outage report](#outage-report)
  * [Capabilities used](#capabilities-used) 
  * [Running in docker-compose](#running-in-docker-compose)

# Description
The objective of `service-outage-monitor` is to monitor edges and make decisions according to the state of these edges.
It appends information related to edge events to Bruin outage tickets, too.

This microservice is in charge of running three processes:
* Outage report. This is a process that reports the set of edges that are both in outage state and with no Bruin ticket
  associated.
* Outage monitoring. This one is in charge of monitoring edges and creating outage tickets if an edge is in outage
  state for a period of time. Existing tickets are resolved and unresolved depending on some conditions, too.
* Triage. This process is aimed at updating existing outage tickets in Bruin with information related to recent edge events.

# Outage report


### Overview
The outage report process aims to detect faulty edges which are not linked in any way to an open
Bruin ticket and send a report with all those edges via e-mail. Note that edges targeted at testing purposes are
not included.

#### Setup velocloud hosts and filters

For development, you can change depending on each instance the different hosts and filters associated to them.
The values should be separated by `:` character `host1:host2`, `filter_host_1:filter_host_2`

```yml
# gitlab-ci/terraform-templates/.gitlab-ci-deploy-templates.yml

- export TF_VAR_SERVICE_OUTAGE_MONITOR_1_HOSTS=${VELOCLOUD_HOST_1}
- export TF_VAR_SERVICE_OUTAGE_MONITOR_1_HOSTS_FILTER=${VELOCLOUD_HOST_1_FILTER}
- export TF_VAR_SERVICE_OUTAGE_MONITOR_2_HOSTS=${VELOCLOUD_HOST_2}
- export TF_VAR_SERVICE_OUTAGE_MONITOR_2_HOSTS_FILTER=${VELOCLOUD_HOST_2_FILTER}
- export TF_VAR_SERVICE_OUTAGE_MONITOR_3_HOSTS="${VELOCLOUD_HOST_3}:${VELOCLOUD_HOST_4}"
- export TF_VAR_SERVICE_OUTAGE_MONITOR_3_HOSTS_FILTER="${VELOCLOUD_HOST_3_FILTER}:${VELOCLOUD_HOST_4_FILTER}"
- export TF_VAR_SERVICE_OUTAGE_MONITOR_4_HOSTS=""
- export TF_VAR_SERVICE_OUTAGE_MONITOR_4_HOSTS_FILTER=""
````

Example values for velocloud host and filter

```
# Gitlab settings CI/CD variables
VELOCLOUD_HOST_1=mettel.velocloud.net
VELOCLOUD_HOST_1_FILTER=[1, 2, 3]

# Local development to add more hosts and filters to a concrete instance
VELOCLOUD_HOSTS="mettel.velocloud.net:metvco02.mettel.net"
VELOCLOUD_HOSTS_FILTER="[1, 2, 3]:[]"
```

For change env files used by [docker-compose](../.docker-compose.yml) it's necessary modify the file [environment_files_generator.py](../installation-utils/environment_files_generator.py) as exposed below:
```
# Service outage monitor hosts filter for service-outage-monitor instances
SERVICE_OUTAGE_MONITOR_1_VELOCLOUD_HOSTS = VELOCLOUD_HOST_1
SERVICE_OUTAGE_MONITOR_1_VELOCLOUD_HOSTS_FILTER = VELOCLOUD_HOST_1_FILTER
SERVICE_OUTAGE_MONITOR_2_VELOCLOUD_HOSTS = VELOCLOUD_HOST_2
SERVICE_OUTAGE_MONITOR_2_VELOCLOUD_HOSTS_FILTER = VELOCLOUD_HOST_2_FILTER
SERVICE_OUTAGE_MONITOR_3_VELOCLOUD_HOSTS = VELOCLOUD_HOST_3 + ':' + VELOCLOUD_HOST_4
SERVICE_OUTAGE_MONITOR_3_VELOCLOUD_HOSTS_FILTER = VELOCLOUD_HOST_3_FILTER + ':' + VELOCLOUD_HOST_4_FILTER
SERVICE_OUTAGE_MONITOR_4_VELOCLOUD_HOSTS = ""
SERVICE_OUTAGE_MONITOR_4_VELOCLOUD_HOSTS_FILTER = ""
```

Also it is necessary to change the desired tasks for each instance, as explained in section [Deploying just a subset of microservices](../README.md#deploying-just-a-subset-of-microservices) of the main README.
If any `service-outage-monitor` instance is not to be used, the value of `service_outage_monitor_<X>_desired_tasks` should be set to 0, being `X` the number of the service-outage-monitor instance that is going to be disabled. 

> At this moment, this process is disabled in production environment because edges in `decomissioned` and
`maintenance` state should not be monitored.

This report is sent **every hour** and contains the list of faulty edges represented as a table like:

| Date of detection | Company | Edge name | Last contact | Serial number   |                                     Edge URL                                 |   Outage causes  |
|:-----------------:|:-------------:|:-----------:|:----------------------------------------------------------------------------:|:----------------:|
|     <detection_date_1>    |   <company_1>  | <edge_name_1> | <last_contact_1> | <serial_number_1> | <edge_url_1> | <outage_causes_list_1> |
|     <detection_date_2>    |   <company_2>  | <edge_name_2> | <last_contact_2> | <serial_number_2> | <edge_url_2> | <outage_causes_list_2> |
|     <detection_date_N>    |   <company_N>  | <edge_name_N> | <last_contact_N> | <serial_number_N> | <edge_url_N> | <outage_causes_list_N> |

where:
- **Date of detection**. Points out when the outage in an edge was first detected. It's a datetime represented with format `YYYY-MM-DD HH:mm:ss`.
- **Company**. The company this edge belongs to.
- **Edge name**. The name of the edge.
- **Last contact**. The moment that the edge was contacted for the last time.
- **Serial number**. The serial number of the faulty edge.
- **Edge URL**. The URL of this edge in the Velocloud system.
- **Outage causes**. The reasons why the edge became faulty. It's a list containing a network element (either a link or the edge itself) and
  the state that caused the outage (as of now, this state is `OFFLINE` for edges and `DISCONNECTED` for links).

Besides this table, the e-mail has a CSV file like the following one attached to it:
```
detection_time,edge_name,enterprise,last_contact,links,serial_number,outage_causes
<detection_date_1>,<edge_name_1>,<last_contact_1>,<company_1>,<edge_url_1>,<serial_number_1>,<comma_separated_causes_1>
<detection_date_2>,<edge_name_2>,<last_contact_2>,<company_2>,<edge_url_2>,<serial_number_2>,<comma_separated_causes_2>
<detection_date_N>,<edge_name_N>,<last_contact_N><company_N>,<edge_url_N>,<serial_number_N>,<comma_separated_causes_N>
```

### Work Flow

#### Considerations
The outage report process is divided into three APScheduler jobs that communicate through a Redis instance. Bear in mind these two
terms to understand the role of every job:
- **Quarantine**. The quarantine is a subset of Redis keys that start with the prefix `EDGES_QUARANTINE`.
- **Reporting queue**. The reporting queue is a subset of Redis keys that start with the prefix `EDGES_TO_REPORT`.

#### Outage detector job
This job runs **every 40 minutes** and is in charge of claiming the status of all the edges from the Velocloud API that belong to
the enterprises under monitoring.
- If an edge is in `DISCONNECTED` state or any of its links is `OFFLINE`, its status is put into quarantine.
- If that is not the case, then the edge is just ignored as there is no interest in healthy edges for this report.

#### Quarantine job
This one runs **every 10 minutes**. Its duty is to pull all the edges statuses from the Redis quarantine
and check if they are still in an outage state.
- If the edge from quarantine is still in an outage condition and there is no outage ticket open in the Bruin service, then the edge
  is moved from quarantine to the reporting queue.
- Otherwise, no action is applied to this edge. It is just kept into quarantine for the next quarantine job.

> In case of a crash of the `service-outage-monitor` microservice, there is a mechanism implemented that triggers one
job per edge stored in quarantine as soon as the microservice is restarted. This way the quarantine is processed before
pulling edges statuses from the Velocloud API.

#### Reporter job
This job is executed **every hour** and it simply:
- Builds an HTML-formatted text containing a table with all the edges stored in the reporting queue,
- Embeds the text (along with a CSV containing all the info of the faulty edges) into an e-mail, and
- Sends it to the proper recipients.

After that sequence of steps, the reporting queue is cleared up so it does not pollute subsequent reports.

> In case of a crash of the `service-outage-monitor` microservice, edges stored in the reporting queue are sent via e-mail as soon
as the microservice restarts.

# Outage monitoring

### Overview
The objective of the outage monitoring process is to detect edges that remains faulty for a period of time and create outage tickets in Bruin
for them in that case. If these edges are already under an existing outage ticket then the system makes a choice to either resolve
or unresolve it depending on the outage state of the edge.

### Work Flow

This is the algorithm implemented to carry out the monitoring of edges:

#### First traversal of edges
1. For every edge under monitoring
   1. Get its status
   2. Check whether it is in outage state or not
      1. If the edge is in outage state, schedule a re-check in 10 minutes.
      2. If the edge is healthy, skip re-checking it and attempt to autoresolve the outage ticket it is under in
         case it exists.

#### Re-checking an edge that was in outage state
1. Get the status of the edge
2. Check whether if the edge is still in outage state or not
   1. If the edge is still in outage state, the working environment is the `production` one and there is no outage
      ticket created for this edge, then attempt to create an outage ticket.
      
      * If Bruin returns a HTTP response with a 200 status code then it means the ticket was created.
      * If Bruin returns a HTTP response with a 409 status code then it means there is an existing outage ticket with
        In Progress state and hence no additional action is taken.
      * If Bruin returns a HTTP response with a 471 status code then it means there is an existing outage ticket with
        Resolved state and hence the process will attempt to unresolve it.
   2. Otherwise, attempt to autoresolve the outage ticket the edge is under in case it exists.

> Bear in mind that the whole outage monitoring process runs every 3 minutes.

# Triage

### Overview
The objective of the triage process is to update existing outage tickets in Bruin with information related to recent
edge events.

### Work Flow

This is the algorithm implemented to carry out the triage process of edges:

#### Collecting data for the actual processing
1. The process gathers all the edges that need to be monitored and map them by Bruin client ID.
2. All open tickets are retrieved from Bruin.
3. If an open ticket is not linked to one of the edges retrieved in the first step then it is discarded.
4. All the remaining tickets are separated in two different sets: tickets with at least one triage note and 
   tickets without triage notes.
5. Finally, both sets of tickets are processed concurrently.

#### Processing tickets with at least one triage note
1. To simplify the whole process, all non-triage notes are discarded for every ticket.
2. For every one of these tickets:
   1. Look for the most recent triage note
   2. Check if this note was appended recently (30 minutes or less ago)
      1. If so, skip this ticket
      2. If not:
         1. Claim all the events related to the edge under the current ticket for the period between the creation date
            of the most recent triage note and the current moment.
         2. Check if any event was found
            1. If not, skip this ticket
            2. If so, sort all these events by `eventTime` in descendant order (i.e. most recent events come first).
               1. Check if the current environment is PRODUCTION
                  1. If so, append triage notes based on these events to the current ticket. Bruin does not allow appending notes with
                     more than 1500 characters so it may be necessary to split huge notes into smaller notes before sending them
                     to Bruin.
                  2. If not, skip this ticket
               2. Check if any triage note was appended
                  1. If so, deliver a Slack notification to keep the development team posted about the ticket updates
                  2. If not, skip this ticket

#### Processing tickets without triage notes
1. For every one of these tickets:
   1. Claim all the events related to the edge under the current ticket for the period between 7 days ago
      and the current moment.
   2. Check if any event was found
      1. If not, skip this ticket
      2. If so, sort all these events by `eventTime` in descendant order (i.e. most recent events come first).
      3. Check what the current environment is
         1. If it is DEV, compose an e-mail with all the information related to edge events and deliver it to the
            development team
         2. If it is PRODUCTION, append a note to the current ticket with all the information related to edge events

> Bear in mind that the whole triage process runs every 2 minutes.

# Capabilities used
- [Velocloud bridge](../velocloud-bridge/README.md)
- [Bruin bridge](../bruin-bridge/README.md)
- [Notifier](../notifier/README.md)

# Running in docker-compose
`docker-compose up --build redis velocloud-bridge bruin-bridge notifier nats-server service-outage-monitor`

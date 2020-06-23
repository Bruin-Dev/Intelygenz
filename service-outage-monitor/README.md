# Table of contents
  * [Description](#description)
  * [Setting up Velocloud hosts and filters](#setting-up-velocloud-hosts-and-filters)
  * [Outage monitoring](#outage-monitoring)
  * [Triage](#triage)
  * [Capabilities used](#capabilities-used) 
  * [Running in docker-compose](#running-in-docker-compose)

# Description
The objective of `service-outage-monitor` is to monitor edges and make decisions according to the state of these edges.
It appends information related to edge events to Bruin outage tickets, too.

This microservice is in charge of running two processes:
* Outage monitoring. This one is in charge of monitoring edges and creating outage tickets if an edge is in outage
  state for a period of time. Existing tickets are resolved and unresolved depending on some conditions, too.
* Triage. This process is aimed at updating existing outage tickets in Bruin with information related to recent edge events.


# Setting up Velocloud hosts and filters

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

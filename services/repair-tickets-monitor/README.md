# Repair tickets monitor
  * [Architecture](#architecture)
  * [Service general description](#service-general-description)
  * [Monitoring emails](#monitoring-emails)
  * [Sending feedback to KRE](#sending-feedback-to-kre)
  * [Capabilities used](#capabilities-used) 
  * [Running in docker-compose](#running-in-docker-compose)

# Architecture
![RTA diagram](../../docs/img/RTA.jpg)

# Service general description
The goals of this services are:
1. Update bruin platform with the emails tagged by the [email-tagger-monitor](../email-tagger-monitor/README.md)
2. Send feedback of predictions about created tickets and closed tickets

## Process : Repair tickets monitor
The monitoring process runs periodically to look for e-mails recently tagged by the `email-tagger-monitor` in the Redis
instance `redis-email-tagger`. At this moment, only e-mails with the `Repair` tag are useful for the `repair-tickets-monitor`.
If the e-mail was tagged with a tag other than `Repair`, it is dropped from Redis and considered as processed, as there
is nothing to do with it actually.

When an e-mail has the `Repair` tag, its details (body, sender, recipients, etc.) are sent to the KRE along with the
tag. The predictive model will get these inputs and will shortly return a data structure that represents an inference.
An example of this data structure would be:

Sumarly the process get the following relevant data from KRE prediction:
- `potential_service_numbers` is a list of service numbers identified in the body of the e-mail passed to the predictive model.
- `predicted_class` is a string that can take any value of `VOO`, `VAS` and `Other`, and it essentially is a prediction of
  the most appropriate ticket that the service should create or update in Bruin, according to the interpretation the AI model made
  about the discussion in the email body.
  If it takes the value `VOO` or `VAS`, the most appropriate ticket will be a Service Outage or a Service Affecting ticket, respectively.
  On the other hand, the value `Other` means that no appropriate ticket type could be predicted for this e-mail.

Every service number in `potential_service_numbers` is checked to make sure they are registered in Bruin inventories. If a service
number is not in their inventories, it is discarded from the monitoring process as it will impossible to determine who is the
owner of the device at a later point, which is a precondition to create or update tickets.

Then the `repair ticket mnonitor` check if there are tickets to create or uptate, send the feedback to KRE and mark the ticket as completed in redis.

## Process: New created tickets feedback
The responsability of this process is reporting of created tickets to `repair-tickets-kre-bridge`. The process runs periodically to look for tickets marks as archive by the [email-tagger-monitor -> new-ticket-monitor](../email-tagger-monitor/README.md). 
KRE need data to make the most of the feedback, for this reason this process call to bruin to enrich the data before sending.
Then the process send the enriched data to [Repair Tickets KRE bridge](../repair-tickets-kre-bridge/README.md) and delete tag of Redis.

## Process: New closed tickets feedback
The responsability of this process is reporting of closed tickets to `repair-tickets-kre-bridge`. The process runs periodically. In each single run, the process request to Bruin the last 3 days ticket information. Then the process filter the closed ticket to get only the tickets that were created by repair-ticket-monitor. The last taks is send the filtered ticket to repair-ticket-kre-bridge. 

# Capabilities used
- [Repair Tickets KRE bridge](../repair-tickets-kre-bridge/README.md)
- [Bruin bridge](../bruin-bridge/README.md)
- [Notifier](../notifier/README.md)

# Running in docker-compose
1. Spin up the NATS and Redis instances: `docker-compose up --build nats-server redis redis-email-tagger`
2. Spin up the capabilities: `docker-compose --build bruin-bridge repair-tickets-kre-bridge notifier`
3. Spin up the use case: `docker-compose up --build repair-tickets-monitor`

## Bruin-mock in local
TODO: Complete in the another MR

## KRE in local
TODO: Complete in the another MR

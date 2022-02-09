# Table of contents
  * [Description](#description)
  * [Monitoring emails](#monitoring-emails)
  * [Sending feedback to KRE](#sending-feedback-to-kre)
  * [Capabilities used](#capabilities-used) 
  * [Running in docker-compose](#running-in-docker-compose)

# Description
The objective of `repair-tickets-monitor` is to post process e-mails tagged in the service `email-tagger-monitor` to either
create new Service Outage tickets or update existing ones, based on the contents of the e-mail and inferences made by
a predictive AI model running in a Konstellation Runtime Environment (KRE).

Along with ticket manipulation, this service is also in charge of composing data structures based on created and closed
tickets, as well as sending them to the KRE, so they can be ingested as feedback to train the AI model and ultimately
improve the confidence level of the inferences it formulates.

# Monitoring emails

The monitoring process runs periodically to look for e-mails recently tagged by the `email-tagger-monitor` in the Redis
instance `redis-email-tagger`. At this moment, only e-mails with the `Repair` tag are useful for the `repair-tickets-monitor`.
If the e-mail was tagged with a tag other than `Repair`, it is dropped from Redis and considered as processed, as there
is nothing to do with it actually.

When an e-mail has the `Repair` tag, its details (body, sender, recipients, etc.) are sent to the KRE along with the
tag. The predictive model will get these inputs and will shortly return a data structure that represents an inference.
An example of this data structure would be:

```json
{
  "potential_service_numbers": [
    "VC1234567",
    "VC1111111",
    "VC9999999"
  ],
  "predicted_class": "VOO",
  "is_filtered": true,
  "in_validation_set": true,
  "tagger_is_below_threshold": true,
  "rta_model1_is_below_threshold": true,
  "rta_model2_is_below_threshold": true
}
```

where:
- `potential_service_numbers` is a list of service numbers identified in the body of the e-mail passed to the predictive model.
- `predicted_class` is a string that can take any value of `VOO`, `VAS` and `Other`, and it essentially is a prediction of
  the most appropriate ticket that the service should create or update in Bruin, according to the interpretation the AI model made
  about the discussion in the email body.
  
  If it takes the value `VOO` or `VAS`, the most appropriate ticket will be a Service Outage or a Service Affecting ticket, respectively.
  On the other hand, the value `Other` means that no appropriate ticket type could be predicted for this e-mail.
- `is_filtered`
- `in_validation_set`
- `tagger_is_below_threshold`
- `rta_model1_is_below_threshold`
- `rta_model2_is_below_threshold`

Every service number in `potential_service_numbers` is checked to make sure they are registered in Bruin inventories. If a service
number is not in their inventories, it is discarded from the monitoring process as it will impossible to determine who is the
owner of the device at a later point, which is a precondition to create or update tickets.



# Capabilities used
- [Repair Tickets KRE bridge](../repair-tickets-kre-bridge/README.md)
- [Bruin bridge](../bruin-bridge/README.md)
- [Notifier](../notifier/README.md)

# Running in docker-compose

1. Spin up the NATS and Redis instances: `docker-compose up --build nats-server redis redis-email-tagger`
2. Spin up the capabilities: `docker-compose --build bruin-bridge repair-tickets-kre-bridge notifier`
3. Spin up the use case: `docker-compose up --build repair-tickets-monitor`
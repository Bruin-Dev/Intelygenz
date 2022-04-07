# Repair tickets monitor

# Table of contents
* [Description](#description)
* [Work Flow](#work-flow)
* [Capabilities used](#capabilities-used)
* [Running in docker-compose](#running-in-docker-compose)

# Description
This service is responsible for post processing e-mails tagged by the E-mail Tagger Monitor to create Service Outage tickets in Bruin, as long as the AI model living in the KRE instance dictates so through predictions.

# Work Flow

# Capabilities used
- [Bruin Bridge](../bruin-bridge/README.md)
- [Repair tickets KRE bridge](../repair-tickets-kre-bridge/README.md)

![IMAGE: repair-tickets-monitor_microservice_relationships](/docs/img/system_overview/use_cases/repair-tickets-monitor_microservice_relationships.png)

# Running in docker-compose
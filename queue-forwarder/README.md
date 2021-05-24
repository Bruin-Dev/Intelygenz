# Table of contents
  * [Description](#description)
  * [Outage monitoring](#outage-monitoring)
  * [Capabilities used](#capabilities-used) 
  * [Running in docker-compose](#running-in-docker-compose)

# Description
The objective of `queue-forwarder` is...

# Capabilities used
- [Customer cache](../customer-cache/README.md)
- [Bruin bridge](../bruin-bridge/README.md)
- [Notifier](../notifier/README.md)

# Running in docker-compose
`docker-compose up --build redis bruin-bridge notifier nats-server customer-cache queue-forwarder`

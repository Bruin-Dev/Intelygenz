# Table of contents
  * [Description](#description)
  * [Outage monitoring](#outage-monitoring)
  * [Capabilities used](#capabilities-used) 
  * [Running in docker-compose](#running-in-docker-compose)

# Description
The objective of `hawkeye-outage-monitor` is ... [TODO]

# Work Flow
[TODO]

# Capabilities used
- [Hawkeye bridge](../hawkeye-bridge/README.md)
- [Bruin bridge](../bruin-bridge/README.md)
- [Notifier](../notifier/README.md)

# Running in docker-compose
`docker-compose up --build redis hawkeye-bridge bruin-bridge notifier nats-server hawkeye-outage-monitor`

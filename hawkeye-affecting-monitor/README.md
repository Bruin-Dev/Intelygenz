# Table of contents
  * [Description](#description)
  * [Affecting monitoring](#affecting-monitoring)
  * [Capabilities used](#capabilities-used) 
  * [Running in docker-compose](#running-in-docker-compose)

# Description
The objective of `hawkeye-affecting-monitor` is ... [TODO]

# Work Flow
[TODO]

# Capabilities used
- [Hawkeye bridge](../hawkeye-bridge/README.md)
- [Hawkeye customer cache](../hawkeye-customer-cache/README.md)
- [Bruin bridge](../bruin-bridge/README.md)
- [Notifier](../notifier/README.md)

# Running in docker-compose
`docker-compose up --build redis hawkeye-bridge bruin-bridge notifier nats-server hawkeye-customer-cache hawkeye-affecting-monitor`

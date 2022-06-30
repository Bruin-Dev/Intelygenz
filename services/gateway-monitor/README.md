# Table of contents
  * [Description](#description)
  * [Overview](#overview)
  * [Capabilities used](#capabilities-used) 
  * [Running in docker-compose](#running-in-docker-compose)

# Description
The goal of the `gateway-monitoring` service is to monitor the status of gateways and document detected issues on ServiceNow.
A gateway is considered to be having issues if the tunnel count drops by a significant amount within a short period of time.

# Overview
Every few minutes we get two snapshots of the status of all gateways from each VeloCloud host for two different time intervals.
A gateway is considered to be having issues if its tunnel count on the second snapshot is significantly lower than on the first one.
For each unhealthy gateway we call a ServiceNow endpoint that automatically creates, re-opens and/or adds a note to a ticket.

# Capabilities used
- [Velocloud bridge](../velocloud-bridge/README.md)
- [ServiceNow bridge](../servicenow-bridge/README.md)
- [Notifier](../notifier/README.md)

# Running in docker-compose
`docker-compose up --build nats-server redis velocloud-bridge servicenow-bridge notifier gateway-monitor`

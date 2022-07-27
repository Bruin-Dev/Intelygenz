# Table of contents
  * [Description](#description)
  * [Overview](#overview)
  * [Capabilities used](#capabilities-used) 
  * [Running in docker-compose](#running-in-docker-compose)

# Description
The goal of the `gateway-monitoring` service is to monitor the status of gateways and document detected issues on ServiceNow.
A gateway is considered to be having issues if the tunnel count drops by a significant amount within a short period of time.

# Overview
Every few minutes we get the status metrics of all gateways from each VeloCloud host for a recent amount of time.
If the tunnel count of a gateway was significantly lower than average at any point during this period,
we call a ServiceNow endpoint that automatically creates or re-opens a ticket for that gateway.

# Capabilities used
- [Velocloud bridge](../velocloud-bridge/README.md)
- [ServiceNow bridge](../servicenow-bridge/README.md)
- [Notifications bridge](../notifications-bridge/README.md)

# Running in docker-compose
`docker-compose up --build nats-server redis velocloud-bridge servicenow-bridge notifications-bridge gateway-monitor`

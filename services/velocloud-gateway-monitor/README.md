# Table of contents
  * [Description](#description)
  * [Velocloud Gateway monitoring](#velocloud-gateway-monitoring)
  * [Capabilities used](#capabilities-used) 
  * [Running in docker-compose](#running-in-docker-compose)

# Description
The objective of `velocloud-gateway-monitoring` is to monitor gateways status and make decisions according to the metric `tunnelCount`.

This microservice is in charge of running one process:
* Velocloud Gateway monitoing. This one is in charge of monitoring gateways status and checking service now endpoint if a gateway `tunnelCount` threshold 
is less than 20%. It takes one hour and five minutes as samples for checking it.

# Velocloud Gateway monitoring

### Overview
The objective of the velocloud gateway monitoring process is to detect gateways which have a drop in `tunnelCount` in an hour interval and 
check with service now if a ticket exists, or it should create a new one. If it exists it should update it in some way.
All this ticket behaviour is managed automatically by the endpoint once we call it with the `gatewayId`.

### Work Flow

This is the algorithm implemented to carry out the monitoring of gateways status:

#### Checking gateways
1. Get the list of gateways status from the Velocloud host specified in the config for the last hour and the last 5 minutes
2. Check the two data samples are well-formed
3. Distinguish gateways in unhealthy state from healthy gateways
4. For every unhealthy edge:
   1. Attempt to check with service now the status of the ticket and what it should be done

# Capabilities used
- [Velocloud bridge](../velocloud-bridge/README.md)
- [ServiceNow bridge](../servicenow-bridge/README.md)
- [Notifier](../notifier/README.md)

# Running in docker-compose

`docker-compose up --build nats-server redis velocloud-bridge servicenow-bridge notifier velocloud-gateway-monitor`
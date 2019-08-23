# Table of contents
  * [Description](#description)
  * [Work Flow](#work-flow)
  * [Behaviour in dev and in pro](#behaviour-in-development-and-in-production)
  * [Capabilities used](#capabilities-used) 
  * [Running in docker-compose](#running-in-docker-compose)

# Description
The service affecting monitor is currently used to monitor an edge's behaviour, in order to detect if its latency,
packet loss, jitter, utilization exceeds a given threshold. If it does then an email is sent out or a ticket is created.
# Work Flow
Every minute the apscheduler calls service-affecting-monitor's `_service_affecting_monitor_process` function. In this 
function, An rpc call is made to the velocloud bridge to get the edge status, link status (within an interval of 15 minutes),
and enterprise name. 

We then loop through all the links returned from the rpc request. Each iteration we call the function `_latency_check`. 
Here we check the type of link whether its wireless with `serviceGroups` value of `PUBLIC_WIRELESS`, or wired with
 with `serviceGroups` value of `PUBLIC_WIRED` or `PRIVATE_WIRED`. Then we check if either `bestLatencyMsRx` or 
 `bestLatencyMsTx` exceeds the threshold for wireless (120) or wired (50).
 
 If it does exceed then we make a call to `_notify_trouble` which should determine whether we're in development or 
 production. Based on the environment it should either call `_compose_email_object` and send an email if in dev or create a ticket if in
 production. 
 
# Behaviour in development and in production
Currently we can only send emails. So `_notify_trouble` will send emails whether or not we're in development or production.

# Capabilities used
- [Velocloud bridge](../velocloud-bridge/README.md)
- [Notifier](../notifier/README.md)
# Running in docker-compose
`docker-compose up --build nats-streaming velocloud-bridge notifier service-affecting-monitor`
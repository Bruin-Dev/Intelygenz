# Hawkeye outage monitor
* [Description](#description)
* [Workflow](#workflow)
* [Capabilities used](#capabilities-used) 
* [Running in docker-compose](#running-in-docker-compose)

# Description
The objective of `hawkeye-outage-monitor` is to detect devices that remains faulty for a period of time and create outage tickets in Bruin
for them in that case. If these devices are already under an existing outage ticket then the system makes a choice to either resolve
or unresolve it depending on the outage state of the device.

> Bear in mind that the whole outage monitoring process runs every 3 minutes.

# Workflow
## First traversal of devices
1. Get the cache of customers for Hawkeye devices
2. Get the list of probes from Hawkeye
3. Filter probes related to those devices in the cache of customers
4. Distinguish devices in outage state from healthy devices
5. Schedule a re-check job for all the devices in outage state so its state is checked again in a few moments
6. For every healthy device:
   1. Attempt to autoresolve the outage ticket it is under, in case it exists.

## Re-checking a device that was in outage state
1. Get the list of probes from Hawkeye
2. Filter probes related to the devices in the list of devices that were scheduled for re-check
   in the previous step of the process.
3. Distinguish devices in outage state from healthy devices
4. For every device in outage state:
   1. If the working environment is `production` and there is no outage
      ticket created for this device, then attempt to create an outage ticket.

      * If Bruin returns a HTTP response with a 200 status code then it means the ticket was created.
      * If Bruin returns a HTTP response with a 409 status code then it means there is an existing outage ticket with
       In Progress state and hence no additional action is taken.
      * If Bruin returns a HTTP response with a 471 status code then it means there is an existing outage ticket with
       Resolved state and hence the process will attempt to unresolve it.
6. For every healthy device:
   1. Attempt to autoresolve the outage ticket it is under, in case it exists.

# Capabilities used
- [Hawkeye customer cache](../hawkeye-customer-cache/README.md)
- [Notifier](../notifier/README.md)
- [Hawkeye bridge](../hawkeye-bridge/README.md)
- [Bruin bridge](../bruin-bridge/README.md)

![IMAGE: hawkeye-outage-monitor_microservice_relationships](/docs/img/system_overview/use_cases/hawkeye-outage-monitor_microservice_relationships.png)

# Running in docker-compose
`docker-compose up --build redis hawkeye-bridge bruin-bridge notifier nats-server hawkeye-customer-cache hawkeye-outage-monitor`

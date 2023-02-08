# Common On-Call requests

## Auto-resolve a bunch of ticket tasks in a row

Ticket tasks can be auto-resolved for a particular set of ticket IDs by using a script located at the automation-engine repository, right inside the [on-call](scripts/on-call/) folder.

Follow these steps to run it:
- Install poetry in your local environment. Installation guide is available [here](https://python-poetry.org/docs/#installation).
- Run `cd scripts/on-call/ && poetry install` to set up the Poetry virtual environment and dependencies.
- Spin up NATS and the bruin-bridge locally by running `docker-compose up --build nats-server bruin-bridge`.
- Edit the [script](scripts/on-call/autoresolve_tickets.py) to specify the set of ticket IDs you’d like to auto-resolve tasks for.
- Finally, run the script with the command poetry run `autoresolve_tickets.py` and wait for completion.

NOTE: all these steps are documented [here](scripts/on-call/README.md)

## Extend the time the IPA system has to auto-resolve a ticket task in the current documentation cycle

Extending this interval is as easy as editing a configuration value in AWS Parameter Store.

Depending on the service, we will have to edit a parameter or another:
- Ixia / Hawkeye - Service Outage Monitoring
  - Grace Period: `/automation-engine/common/hawkeye-outage-monitor/grace-period-to-autoresolve-after-last-documented-outage`

- InterMapper - Service Outage Monitoring
  - Day Work Schedule:  `/automation-engine/common/intermapper-outage-monitor/grace-period-to-autoresolve-after-last-documented-outage-day-time`
  - Night Work Schedule: `/automation-engine/common/intermapper-outage-monitor/grace-period-to-autoresolve-after-last-documented-outage-night-time`

- VeloCloud - Service Affecting Monitoring
  - Day Work Schedule: `/automation-engine/common/service-affecting/monitor/grace-period-to-autoresolve-after-last-documented-trouble-day-time`
  - Night Work Schedule: `/automation-engine/common/service-affecting/monitor/grace-period-to-autoresolve-after-last-documented-trouble-night-time`

- VeloCloud - Service Outage Monitoring
  - Day Work Schedule: `/automation-engine/common/service-outage/monitor/grace-period-to-autoresolve-after-last-documented-outage-day-time`
  - Night Work Schedule: `/automation-engine/common/service-outage/monitor/grace-period-to-autoresolve-after-last-documented-outage-night-time`

By editing these parameters, the IPA system will have more time to assist Support teams in the event of a huge influx of tickets coming into work queues such as the HNOC one.

## Increase the number of max auto-resolves per ticket task

Extending this max auto-resolution threshold is as easy as editing a configuration value in AWS Parameter Store.

Depending on the service, we will have to edit a parameter or another:
- Ixia / Hawkeye - Service Outage Monitoring
  - The max auto-resolution threshold was never made configurable for this service.

- InterMapper - Service Outage Monitoring
  - `/automation-engine/common/intermapper-outage-monitor/max-autoresolves-per-ticket`

- VeloCloud - Service Affecting Monitoring
  - `/automation-engine/common/service-affecting/monitor/max-autoresolves-per-ticket`

- VeloCloud - Service Outage Monitoring
  - `/automation-engine/common/service-outage/monitor/max-autoresolves-per-ticket`

By editing these parameters, the IPA system will have more time to assist Support teams in the event of a huge influx of tickets coming into work queues such as the HNOC one.

## Extend Service Affecting thresholds for VeloCloud monitoring

Extending these thresholds is as easy as editing configuration values in AWS Parameter Store.

- Depending on the Service Affecting trouble, we will have to edit a parameter or another:
  - Latency: `/automation-engine/common/service-affecting/monitor/latency-monitoring-threshold`

  - Packet Loss: `/automation-engine/common/service-affecting/monitor/packet-loss-monitoring-threshold`

  - Jitter: `/automation-engine/common/service-affecting/monitor/jitter-monitoring-threshold`

  - Bandwidth Over-Utilization: `/automation-engine/common/service-affecting/monitor/bandwidth-over-utilization-monitoring-threshold`
  
  - Circuit Instability: `/automation-engine/common/service-affecting/monitor/circuit-instability-monitoring-threshold`

By editing these parameters, the IPA system can be more or less sensitive to Service Affecting troubles spotted while monitoring VeloCloud edges.

## Disable the quarantine in Service Outage Monitor services

Disabling these quarantines is as easy as editing configuration values in AWS Parameter Store to set them to 0 seconds.

Depending on the service, we will have to edit a parameter or another:
- Ixia / Hawkeye - Service Outage Monitoring
  - `/automation-engine/common/hawkeye-outage-monitor/quarantine-for-devices-in-outage`

- VeloCloud - Service Outage Monitoring
  - Outage Type - Hard Down with HA enabled: `/automation-engine/common/service-outage/monitor/quarantine-for-edges-in-ha-hard-down-outage`
  - Outage Type - Link Down with HA enabled: `/automation-engine/common/service-outage/monitor/quarantine-for-edges-in-ha-link-down-outage`
  - Outage Type - Soft Down with HA enabled: `/automation-engine/common/service-outage/monitor/quarantine-for-edges-in-ha-soft-down-outage`
  - Outage Type - Hard Down with HA disabled: `/automation-engine/common/service-outage/monitor/quarantine-for-edges-in-hard-down-outage`
  - Outage Type - Link Down with HA disabled: `/automation-engine/common/service-outage/monitor/quarantine-for-edges-in-link-down-outage`

By editing these parameters, the IPA system can assist Support teams better when there are massive outages across multiple sites and there is no time to wait to report them to Bruin.

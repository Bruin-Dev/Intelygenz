# Task Forwards #

**Metric name:** tasks_forwarded

**Metric type:** Counter

**Data store:** Prometheus

## Service Outage Monitor ##

**Description:** Number of service outage tasks related to VeloCloud edges that have been forwarded by the `service-outage-monitor`.

**Labels:**

- **feature:** Service Outage Monitor
- **system:** VeloCloud
- **topic:** VOO
- **client:** [<client\> | FIS | Other]
- **host:** <host\>
- **outage_type:** [Hard Down (no HA) | Hard Down (HA) | Soft Down (HA) | Link Down (no HA) | Link Down (HA)]
- **severity:** [2 | 3]
- **has_digi:** [True | False]
- **has_byob:** [True | False]
- **link_types:** [Wired | Wireless | Both | None]
- **target_queue:** [HNOC Investigate | ASR Investigate | Wireless Repair Intervention Needed]

## Service Affecting Monitor ##

**Description:** Number of service affecting tasks related to VeloCloud edges that have been forwarded by the `service-affecting-monitor`.

**Labels:**

- **feature:** Service Affecting Monitor
- **system:** VeloCloud
- **topic:** VAS
- **client:** [<client\> | FIS | Other]
- **host:** <host\>
- **severity:** 3
- **trouble:** [Latency | Packet Loss | Jitter | Bandwidth Over Utilization | Circuit Instability]
- **has_byob:** [True | False]
- **link_types:** [Wired | Wireless]
- **target_queue:** [HNOC Investigate | ASR Investigate]

## InterMapper Outage Monitor ###

**Description:** Number of service outage tasks related to InterMapper devices that have been forwarded by the `intermapper-outage-monitor`.

**Labels:**

- **feature:** InterMapper Outage Monitor
- **system:** InterMapper
- **topic:** VOO
- **severity:** 2
- **event:** <event\>
- **is_piab:** [True | False]
- **target_queue:** [HNOC Investigate | IPA Investigate]

## Fraud Monitor ##

**Description:** Number of service affecting tasks related to Fraud alerts that have been forwarded by the `fraud-monitor`.

**Labels:**

- **feature:** Fraud Monitor
- **system:** MetTel Fraud Alerts
- **topic:** VAS
- **severity:** 3
- **trouble:** [Possible Fraud | Request Rate Monitor Violation]
- **target_queue:** HNOC Investigate

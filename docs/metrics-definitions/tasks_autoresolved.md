# Task Auto-Resolves #

**Metric name:** tasks_autoresolved

**Metric type:** Counter

**Data store:** Prometheus

## Service Outage Monitor ##

**Description:** Number of service outage tasks related to VeloCloud edges that have been auto-resolved by the `service-outage-monitor`.

**Labels:**

- **feature:** Service Outage Monitor
- **system:** VeloCloud
- **topic:** VOO
- **client:** [<client\> | FIS | Other]
- **host:** <host\>
- **outage_type:** [Hard Down (no HA) | Hard Down (HA) | Soft Down (HA) | Link Down (no HA) | Link Down (HA) | Unknown]
- **severity:** [2 | 3]
- **has_digi:** [True | False | Unknown]
- **has_byob:** [True | False | Unknown]
- **link_types:** [Wired | Wireless | Both | None | Unknown]

## Service Affecting Monitor ##

**Description:** Number of service affecting tasks related to VeloCloud edges that have been auto-resolved by the `service-affecting-monitor`.

**Labels:**

- **feature:** Service Affecting Monitor
- **system:** VeloCloud
- **topic:** VAS
- **client:** [<client\> | FIS | Other]
- **host:** <host\>
- **severity:** 3
- **trouble:** [Latency | Packet Loss | Jitter | Bandwidth Over Utilization | Circuit Instability | Multiple | Unknown]
- **has_byob:** [True | False]
- **link_types:** [Wired | Wireless | Unknown]

## InterMapper Outage Monitor ##

**Description:** Number of service outage tasks related to InterMapper devices that have been auto-resolved by the `intermapper-outage-monitor`.

**Labels:**

- **feature:** InterMapper Outage Monitor
- **system:** InterMapper
- **topic:** VOO
- **severity:** 2
- **event:** <event\>
- **is_piab:** [True | False]

## TNBA Monitor ##

**Description:** Number of tasks related to VeloCloud edges that have been auto-resolved by the `tnba-monitor`.

**Labels:**

- **feature:** TNBA Monitor
- **system:** VeloCloud
- **topic:** [VOO | VAS]
- **client:** [<client\> | FIS | Other]
- **host:** <host\>
- **severity:** [2 | 3]

## Hawkeye Outage Monitor ##

**Description:** Number of service outage tasks related to Ixia probes that have been auto-resolved by the `hawkeye-outage-monitor`.

**Labels:**

- **feature:** Hawkeye Outage Monitor
- **system:** Ixia
- **topic:** VOO
- **client:** [<client\> | FIS | Other]
- **outage_type:** [Node To Node | Real Service | Both | None | Unknown]
- **severity:** 2

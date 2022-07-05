# Task Creations #

**Metric name:** tasks_reopened

**Type of metric:** Counter

**Data store:** Prometheus

## VeloCloud - Service Outage tasks re-opened ##

**Description:** This metric counts how many Service Outage tasks related to VeloCloud edges have been re-opened since the service-outage-monitor instances started until now.

**Labels:**
- feature: Service Outage Monitor
- system: VeloCloud
- topic: VOO
- client: _<one of the relevant clients defined in AWS\>_
- host: [mettel.velocloud.net | metvco02.mettel.net | metvco03.mettel.net | metvco04.mettel.net]
- outage_type: [Hard Down (no HA) | Hard Down (HA) | Soft Down (HA) | Link Down (no HA) | Link Down (HA)]
- severity: [2 | 3]
- has_digi: [True | False]
- has_byob: [True | False]
- link_types: [Wired | Wireless | Both]

## Ixia - Service Outage tasks re-opened ##

**Description:** This metric counts how many Service Outage tasks related to Ixia probes have been re-opened since the hawkeye-outage-monitor instances started until now.

**Labels:**
- feature: Hawkeye Outage Monitor
- system: Ixia
- topic: VOO
- client: _<one of the relevant clients defined in AWS\>_
- outage_type: [Node To Node | Real Service | Both]
- severity: 2

## InterMapper - Service Outage tasks re-opened ##

**Description:** This metric counts how many Service Outage tasks related to InterMapper devices have been re-opened since the intermapper-outage-monitor started until now.

**Labels:**
- feature: InterMapper Outage Monitor
- system: InterMapper
- topic: VOO
- severity: 2
- event: [Up | OK | Down | Critical | Alarm | Warning | Link Warning]
- is_piab: [True | False]

## VeloCloud - Service Affecting tasks re-opened ##

**Description:** This metric counts how many Service Affecting tasks related to VeloCloud edges have been re-opened since the service-affecting-monitor instances started until now.

**Labels:**
- feature: Service Affecting Monitor
- system: VeloCloud
- topic: VAS
- client: _<one of the relevant clients defined in AWS\>_
- host: [mettel.velocloud.net | metvco02.mettel.net | metvco03.mettel.net | metvco04.mettel.net]
- severity: 3
- trouble: [Jitter | Latency | Packet Loss | Bandwidth Over Utilization | Circuit Instability]

## Fraud - Service Affecting tasks re-opened ##

**Description:** This metric counts how many Service Affecting tasks related to Fraud alerts have been re-opened since the fraud-monitor started until now.

**Labels:**
- feature: Fraud Monitor
- system: MetTel Fraud Alerts
- topic: VAS
- severity: 3
- trouble: [Possible Fraud | Request Rate Monitor Violation]

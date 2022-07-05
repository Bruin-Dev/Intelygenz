# Task Auto-resolves #

**Metric name:** tasks_autoresolved

**Type of metric:** Counter

**Data store:** Prometheus

## VeloCloud  - Service Outage tasks auto-resolved ##

**Description:** This metric counts how many Service Outage tasks in progress related to VeloCloud edges have been auto-resolved since the service-outage-monitor instances started until now.

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

## Ixia - Service Outage tasks auto-resolved ##

**Description:** This metric counts how many Service Outage tasks in progress related to Ixia probes have been auto-resolved since the hawkeye-outage-monitor started until now.

**Labels:**
- feature: Hawkeye Outage Monitor
- system: Ixia
- topic: VOO
- client: _<one of the relevant clients defined in AWS\>_
- severity: 2

## InterMapper - Service Outage tasks auto-resolved ##

**Description:** This metric counts how many Service Outage tasks in progress related to InterMapper devices have been auto-resolved since the intermapper-outage-monitor started until now.

**Labels:**
- feature: InterMapper Outage Monitor
- system: InterMapper
- topic: VOO
- severity: 2
- event: [Up | OK | Down | Critical | Alarm | Warning | Link Warning]
- is_piab: [True | False]

## VeloCloud - Service Affecting tasks auto-resolved ##

**Description:** This metric counts how many Service Affecting tasks in progress related to VeloCloud edges have been auto-resolved since the service-affecting-monitor instances started until now.

**Labels:**
- feature: Service Affecting Monitor
- system: VeloCloud
- topic: VAS
- client: _<one of the relevant clients defined in AWS\>_
- host: [mettel.velocloud.net | metvco02.mettel.net | metvco03.mettel.net | metvco04.mettel.net]
- severity: 3

## AI-powered - Service Outage tasks auto-resolved ##

**Description:** This metric counts how many Service Outage tasks in progress related to VeloCloud edges have been auto-resolved since the tnba-monitor started until now.

**Labels:**
- feature: TNBA Monitor
- system: VeloCloud
- topic: VOO
- client: _<one of the relevant clients defined in AWS\>_
- host: [mettel.velocloud.net | metvco02.mettel.net | metvco03.mettel.net | metvco04.mettel.net]
- outage_type: [Hard Down (no HA) | Hard Down (HA) | Soft Down (HA) | Link Down (no HA) | Link Down (HA)]
- severity: 2
- has_digi: [True | False]
- has_byob: [True | False]
- link_types: [Wired | Wireless | Both]

## AI-powered - Service Affecting tasks auto-resolved ##

**Description:** This metric counts how many Service Affecting tasks in progress related to VeloCloud edges have been auto-resolved since the tnba-monitor started until now.

**Labels:**
- feature: TNBA Monitor
- system: VeloCloud
- topic: VAS
- client: _<one of the relevant clients defined in AWS\>_
- host: [mettel.velocloud.net | metvco02.mettel.net | metvco03.mettel.net | metvco04.mettel.net]
- severity: 3

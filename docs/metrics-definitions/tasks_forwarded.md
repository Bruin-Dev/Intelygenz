# Task Forwards #

**Metric name:** tasks_forwarded

**Type of metric:** Counter

**Data store:** Prometheus

## VeloCloud - Service Outage tasks forwarded to HNOC Investigate queue ##

**Description:** This metric counts how many Service Outage tasks in progress related to VeloCloud edges have been forwarded to the HNOC Investigate queue since the service-outage-monitor instances started until now.

**Labels:**
- feature: Service Outage Monitor
- system: VeloCloud
- topic: VOO
- client: _<one of the relevant clients defined in AWS\>_
- host: [mettel.velocloud.net | metvco02.mettel.net | metvco03.mettel.net | metvco04.mettel.net]
- outage_type: [Hard Down Outage (no HA) | Hard Down Outage (HA) | Soft Down Outage (HA) | Link Down Outage (no HA) | Link Down Outage (HA)]
- severity: [2 | 3]
- target_queue: HNOC Investigate

## VeloCloud  - Service Outage tasks forwarded to Wireless Repair Intervention Needed queue ##

**Description:** This metric counts how many Service Outage tasks in progress related to VeloCloud edges with at least one disconnected DiGi link have been forwarded to the Wireless Repair Intervention Needed queue after a failed DiGi reboot since the service-outage-monitor instances started until now.

**Labels:**
- feature: Service Outage Monitor
- system: VeloCloud
- topic: VOO
- client: _<one of the relevant clients defined in AWS\>_
- host: [mettel.velocloud.net | metvco02.mettel.net | metvco03.mettel.net | metvco04.mettel.net]
- outage_type: [Link Down Outage (no HA) | Link Down Outage (HA)]
- severity: 3
- has_digi: True
- has_byob: [True | False]
- link_types: Wireless
- target_queue: Wireless Repair Intervention Needed

## VeloCloud - Service Outage tasks forwarded to ASR Investigate queue ##

**Description:** This metric counts how many Service Outage tasks in progress related to VeloCloud edges with at least one wired disconnected link that is not BYOB, Customer Owned or a PIAB have been forwarded to the ASR Investigate queue since the service-outage-monitor instances started until now.

**Labels:**
- feature: Service Outage Monitor
- system: VeloCloud
- topic: VOO
- client: _<one of the relevant clients defined in AWS\>_
- host: [mettel.velocloud.net | metvco02.mettel.net | metvco03.mettel.net | metvco04.mettel.net]
- outage_type: [Link Down Outage (no HA) | Link Down Outage (HA)]
- severity: 3
- has_digi: [True | False]
- has_byob: False
- link_types: Wired
- target_queue: ASR Investigate

## VeloCloud - Service Affecting tasks forwarded to HNOC Investigate queue ##

**Description:** This metric counts how many Service Affecting tasks in progress related to VeloCloud edges with a jitter, latency, packet loss or bandwidth over utilization issue have been forwarded to the HNOC Investigate queue since the service-affecting-monitor instances started until now.

**Labels:**
- feature: Service Affecting Monitor
- system: VeloCloud
- topic: VAS
- client: _<one of the relevant clients defined in AWS\>_
- host: [mettel.velocloud.net | metvco02.mettel.net | metvco03.mettel.net | metvco04.mettel.net]
- severity: 3
- trouble: [Jitter | Latency | Packet Loss | Bandwidth Over Utilization]
- target_queue: HNOC Investigate

## VeloCloud - Service Affecting tasks forwarded to ASR Investigate queue ##

**Description:** This metric counts how many Service Affecting tasks in progress related to VeloCloud edges related to a non BYOB or Customer Owned wired link with a circuit instability issue have been forwarded to the ASR Investigate queue since the service-affecting-monitor instances started until now.

**Labels:**
- feature: Service Affecting Monitor
- system: VeloCloud
- topic: VAS
- client: _<one of the relevant clients defined in AWS\>_
- host: [mettel.velocloud.net | metvco02.mettel.net | metvco03.mettel.net | metvco04.mettel.net]
- severity: 3
- trouble: Circuit Instability
- target_queue: ASR Investigate

## Fraud - Service Affecting tasks forwarded to HNOC Investigate queue ##

**Description:** This metric counts how many Service Affecting tasks in progress related to Fraud alerts have been forwarded to the HNOC Investigate queue since the fraud-monitor started until now.

**Labels:**
- feature: Fraud Monitor
- system: MetTel Fraud Alerts
- topic: VAS
- severity: 3
- trouble: [Possible Fraud | Request Rate Monitor Violation]
- target_queue: HNOC Investigate

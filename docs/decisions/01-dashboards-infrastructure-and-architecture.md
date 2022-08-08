# **1: Design of an isolated an unique dashboard user experience**

**Status:** Approved

**Decision:** Future is to have an external Grafana that connects to an external Prometheus & InfluxDB 2

Implementation plan as following:
- Prometheus will be deployed as an AWS Managed Prometheus.
- Grafana will be deployed independently in AWS pointing to AWS Prometheus.
- Konstellation KRE will be merged to a single KRE instance as soon as KRE allows it.
- KRE will use a dedicated InfluxDB2 in AWS.
- Grafana will connect to InfluxDB2 as additional data source.
- Chronograf dashboards will be migrated to the dedicated Grafana in AWS.

Miro diagram of affected systems: https://miro.com/app/board/uXjVO6bg-zY=/

**Alternatives considered:** 

**Justification:** 

- Current dashboarding solution has several different interfaces, this is confusing for all kind of users.
- Current stability of dashboarding is dependent in the stability of our K8s deployments, losing all visibility if anything goes wrong on K8s.
- License limitations on InfluxDB OSS1 could become a problem.

**Consequences:**

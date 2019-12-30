<div align="center">
<img src="https://media.licdn.com/dms/image/C4E0BAQHrME9aCW6ulg/company-logo_200_200/0?e=2159024400&v=beta&t=6xMNS1zK1F8asBlM16EzbJ4Im7SlQ8L7a7sgcaNzZQE"  width="200" height="200">
</div>

# Metrics-dashboard<a name="metrics_dashboard"></a>

This module is used for the collection and visualization of metrics, using a set of tools that will be explained below.

**Table of contents**

- [Prometheus](#prometheus)
  - [Configuration](#prometheus_configuration)
- [Thanos](#thanos)
  - [Thanos sidecar](#thanos-sidecar)
    - [Configuration](#thanos_sidecar_configuration)
  - [Thanos store](#thanos-store)
    - [Configuration](#thanos_store_configuration)
  - [Thanos querier](#thanos-querier)
    - [Configuration](#thanos-querier-configuration)
- [Grafana](#grafana)
  - [Configuration](#grafana_configuration)

## Prometheus<a name="prometheus"></a>

[Prometheus](https://github.com/prometheus) is an open-source systems monitoring and alerting toolkit.

This tool is used in the project to obtain metrics of the microservices present in the project.

### Configuration<a name="prometheus_configuration"></a>

A `Dockerfile` of this tool is available in the [prometheus](./prometheus) folder, as well as the necessary configuration files to use it.

In the [configuration files](./prometheus/configs) of Prometheus, it is indicated from which microservices it is desired to scrape metrics, indicating for each of them the necessary connection endpoint.

>At the moment, Prometheus is used to collect metrics from the `sites-monitor` microservice, using the DNS address of the AWS Route53 service as connection endpoint.

## Thanos

[Thanos](https://github.com/thanos-io/thanos) is a set of components that can be composed into a highly available metric system with unlimited storage capacity, which can be added seamlessly on top of existing Prometheus deployments.

The components of Thanos currently in use are listed below.

### Thanos sidecar

The [sidecar](https://github.com/thanos-io/thanos/blob/master/docs/components/sidecar.md) component process runs alongside the Prometheus server and ships new metrics off to the object storage bucket.

#### Configuration<a name="thanos_sidecar_configuration"></a>

There is a [Dockerfile](./thanos/Dockerfile) in which the copy of the configuration file is made, where the bucket in which the metrics will be stored is specified. In this Dockerfile also GRPC and HTTP ports are exposed, obtained through arguments in the build process.

### Thanos store

The [store](https://github.com/thanos-io/thanos/blob/master/docs/components/store.md) component provides a queryable interface to the remotely-stored metrics.

#### Configuration <a name="thanos_store_configuration"></a>
There is a [Dockerfile](./thanos/Dockerfile) in which the copy of the configuration file is made, where the bucket in which the metrics are stored for query them. In this Dockerfile also GRPC and HTTP ports are exposed, obtained through arguments in the build process.

### Thanos querier

The [querier](https://github.com/thanos-io/thanos/blob/master/docs/components/query.md) component provides the interface you’ll talk to from Grafana.

#### Configuration<a name="thanos_querier_configuration"></a>

There is a [Dockerfile](./thanos/Dockerfile-thanos_querier) in which GRPC and HTTP ports are exposed, obtained through arguments in the build process.

## Grafana

Grafana is a tool for query, visualize, alert on and understand metrics.

Grafana is used in the project for the visualization of metrics through a set of dashboards.

### Configuration<a name="grafana_configuration"></a>

There is a [Dockerfile](./grafana/Dockerfile) in which the copy of the configuration files is made.

The thanos-querier instance of the environment will be used as a data source for Grafana dashboards.
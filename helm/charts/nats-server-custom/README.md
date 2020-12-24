# nats-server-custom

![Version: 0.1.0](https://img.shields.io/badge/Version-0.1.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 2.1.9](https://img.shields.io/badge/AppVersion-2.1.9-informational?style=flat-square)

A Helm chart for Kubernetes to deploy nats-server

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| https://nats-io.github.io/k8s/helm/charts/ | nats | 0.7.2 |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| nats.cluster.enabled | bool | `true` |  |
| nats.natsbox.enabled | bool | `false` |  |


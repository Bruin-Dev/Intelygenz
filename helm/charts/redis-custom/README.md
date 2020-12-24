# redis-custom

![Version: 0.1.0](https://img.shields.io/badge/Version-0.1.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 4.4.4](https://img.shields.io/badge/AppVersion-4.4.4-informational?style=flat-square)

A Helm chart for Kubernetes

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| https://kubernetes-charts.storage.googleapis.com/ | redis-ha | 4.4.4 |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| redis-ha.exporter.enabled | bool | `true` |  |
| redis-ha.persistentVolume.enabled | bool | `false` |  |
| redis-ha.replicas | int | `1` |  |


# bouncing-detector-3

![Version: 0.1.0](https://img.shields.io/badge/Version-0.1.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 1.16.0](https://img.shields.io/badge/AppVersion-1.16.0-informational?style=flat-square)

A Helm chart for Kubernetes to deploy microservice bouncing-detector with Velocloud host 3 configuration

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object | `{}` |  |
| autoscaling.enabled | bool | `false` |  |
| autoscaling.maxReplicas | int | `100` |  |
| autoscaling.minReplicas | int | `1` |  |
| autoscaling.targetCPUUtilizationPercentage | int | `80` |  |
| config.capabilities_enabled.bruin_bridge | bool | `true` | Indicate is bruin-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the bruin-bridge service responds correctly to healthcheck calls. |
| config.capabilities_enabled.hawkeye_bridge | bool | `true` | Indicate is hawkeye-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the hawkeye-bridge service responds correctly to healthcheck calls. |
| config.capabilities_enabled.notifier | bool | `true` | Indicate is notifier is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the notifier service responds correctly to healthcheck calls. |
| config.capabilities_enabled.t7_bridge | bool | `true` | Indicate is t8-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the t7-bridge service responds correctly to healthcheck calls. |
| config.capabilities_enabled.velocloud_bridge | bool | `true` | Indicate is velocloud-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the velocloud-bridge service responds correctly to healthcheck calls. |
| config.enable_triage_monitoring | string | `"0"` |  |
| config.velocloud_hosts | string | `"host3"` | Velocloud hosts |
| config.velocloud_hosts_filter | string | `"host3_filter"` | Filter for Velocloud hosts |
| enabled | bool | `true` |  |
| global | object | `{"current_environment":"dev","ecr_registry":{"name":"ecr-registry"},"environment":"automation-test","mode":"aws","nats_server":"nats://nats:4222","papertrail_active":"False","papertrail_host":"logs.papertrailapp.com","papertrail_port":"0","redis_hostname":"redis"}` | Global configuration |
| global.current_environment | string | `"dev"` | Name of environment for EKS cluster and network resources |
| global.ecr_registry.name | string | `"ecr-registry"` | Name of the imagePullSecret created to access the images stored in ECR. |
| global.environment | string | `"automation-test"` | Name of environment for helm charts and redis elasticaches used |
| global.mode | string | `"aws"` | Indicates if the helm chart will be displayed in an aws or local environment, in case it is local, a specific imagePullSecret will be used to access the images stored in ECR. |
| global.nats_server | string | `"nats://nats:4222"` | NATS cluster endpoint used by bruin-bridge |
| global.papertrail_active | string | `"False"` | Indicates if the logs will be sent to papertrail or not. |
| global.papertrail_host | string | `"logs.papertrailapp.com"` | Papertrail host to which the logs will be sent |
| global.papertrail_port | string | `"0"` | Papertrail port to which the logs will be sent |
| global.redis_hostname | string | `"redis"` | Redis Hostname used to store heavy NATS messages (>1MB) |
| image.pullPolicy | string | `"IfNotPresent"` |  |
| image.repository | string | `"374050862540.dkr.ecr.us-east-1.amazonaws.com/bouncing-detector"` |  |
| image.tag | string | `""` |  |
| nodeSelector | object | `{}` |  |
| replicaCount | int | `1` | Number of bouncing-detector-3 pods |
| resources.limits.cpu | string | `"400m"` |  |
| resources.limits.memory | string | `"512Mi"` |  |
| resources.requests.cpu | string | `"200m"` |  |
| resources.requests.memory | string | `"256Mi"` |  |
| service.port | int | `5000` |  |
| service.type | string | `"ClusterIP"` |  |
| tolerations | list | `[]` |  |


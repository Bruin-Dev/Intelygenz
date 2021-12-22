# dri-bridge

![Version: 0.1.0](https://img.shields.io/badge/Version-0.1.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 1.16.0](https://img.shields.io/badge/AppVersion-1.16.0-informational?style=flat-square)

A Helm chart for Kubernetes

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object | `{}` |  |
| autoscaling.enabled | bool | `false` |  |
| autoscaling.maxReplicas | int | `100` |  |
| autoscaling.minReplicas | int | `1` |  |
| autoscaling.targetCPUUtilizationPercentage | int | `80` |  |
| config.digi_base_url | string | `""` | Base URL for Digi API |
| config.digi_client_id | string | `""` | Client ID credentials for Digi API |
| config.digi_client_secret | string | `""` | Client Secret credentials for Digi API |
| config.digi_ip_dev | string | `""` | IP for Digi Dev Environment |
| config.digi_ip_pro | string | `""` | IP for Digi Production Environment |
| config.digi_ip_test | string | `""` | IP for Digi Test Environment |
| config.digi_record_name_dev | string | `""` | Record name for Digi Dev Environment |
| config.digi_record_name_pro | string | `""` | Record name for Digi Production Environment |
| config.digi_record_name_test | string | `""` | Record name for Digi Test Environment |
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
| image.repository | string | `"374050862540.dkr.ecr.us-east-1.amazonaws.com/dri-bridge"` |  |
| image.tag | string | `""` |  |
| nodeSelector | object | `{}` |  |
| replicaCount | int | `1` | Number of bruin-bridge pods to do calls to Bruin API. Do not set this below 2 unless is going to deploy in dev or local environment. |
| resources.limits.cpu | string | `"200m"` |  |
| resources.limits.memory | string | `"256Mi"` |  |
| resources.requests.cpu | string | `"100m"` |  |
| resources.requests.memory | string | `"128Mi"` |  |
| service.port | int | `5000` |  |
| service.type | string | `"ClusterIP"` |  |
| tolerations | list | `[]` |  |


# automation-engine

![Version: 0.1.0](https://img.shields.io/badge/Version-0.1.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 1.16.0](https://img.shields.io/badge/AppVersion-1.16.0-informational?style=flat-square)

A Helm chart for Kubernetes to deploy automation-engine project

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| https://nats-io.github.io/k8s/helm/charts/ | nats | 0.7.2 |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object | `{}` |  |
| autoscaling.enabled | bool | `false` |  |
| autoscaling.maxReplicas | int | `100` |  |
| autoscaling.minReplicas | int | `1` |  |
| autoscaling.targetCPUUtilizationPercentage | int | `80` |  |
| bruin_bridge | object | `{"bruin_base_url":"","bruin_base_url_ip":"","bruin_client_id":"","bruin_client_secret":"","bruin_login_url":"","bruin_login_url_ip":"","image":{"pullPolicy":"IfNotPresent","repository":"374050862540.dkr.ecr.us-east-1.amazonaws.com/bruin-bridge","tag":""},"replicaCount":1,"service":{"port":5000,"type":"ClusterIP"}}` | bruin-bridge module specific configuration |
| bruin_bridge.bruin_base_url | string | `""` | Base URL for Bruin API |
| bruin_bridge.bruin_base_url_ip | string | `""` | Base URL for Bruin API (needed only in dev environments) |
| bruin_bridge.bruin_client_id | string | `""` | Client ID credentials for Bruin API |
| bruin_bridge.bruin_client_secret | string | `""` | Client Secret credentials for Bruin API |
| bruin_bridge.bruin_login_url | string | `""` | Login URL for Bruin API |
| bruin_bridge.bruin_login_url_ip | string | `""` | IP of Bruin Login URL (needed only in dev environments) |
| bruin_bridge.image.repository | string | `"374050862540.dkr.ecr.us-east-1.amazonaws.com/bruin-bridge"` | Repository image for bruin-bridge module |
| bruin_bridge.replicaCount | int | `1` | Number of bruin-bridge pods to do calls to Bruin API. Do not set this below 2 unless is going to deploy in dev or local environment. |
| bruin_bridge.service | object | `{"port":5000,"type":"ClusterIP"}` | Service Configuration |
| config.ecr_registry.name | string | `"ecr-registry"` | Name of the imagePullSecret created to access the images stored in ECR. |
| config.environment | string | `"dev"` | Name of environment for EKS cluster and network resources |
| config.environment_name | string | `"automation-test"` | Name of ephemeral environment for helm charts and redis elasticaches used |
| config.mode | string | `"aws"` | Indicates if the helm chart will be displayed in an aws or local environment, in case it is local, a specific imagePullSecret will be used to access the images stored in ECR. |
| config.nats_server | string | `"nats://nats:4222"` | NATS cluster endpoint used by bruin-bridge |
| config.papertrail_active | string | `"False"` | Indicates if the logs will be sent to papertrail or not. |
| config.papertrail_host | string | `"logs.papertrailapp.com"` | Papertrail host to which the logs will be sent |
| config.papertrail_port | string | `"0"` | Papertrail port to which the logs will be sent |
| config.redis_hostname | string | `"redis"` | Redis Hostname used to store heavy NATS messages (>1MB) |
| nats | object | `{"cluster":{"enabled":true},"nameOverride":"nats-server","natsbox":{"enabled":false}}` | nats helm chart configuration |
| nodeSelector | object | `{}` |  |
| replicaCount | int | `1` | Number of bruin-bridge pods to do calls to Bruin API. Do not set this below 2 unless is going to deploy in dev or local environment. |
| resources.limits.cpu | string | `"200m"` |  |
| resources.limits.memory | string | `"256Mi"` |  |
| resources.requests.cpu | string | `"100m"` |  |
| resources.requests.memory | string | `"128Mi"` |  |
| tolerations | list | `[]` |  |


# lit-bridge

![Version: 0.1.0](https://img.shields.io/badge/Version-0.1.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 1.16.0](https://img.shields.io/badge/AppVersion-1.16.0-informational?style=flat-square)

A Helm chart for Kubernetes to deploy microservice lit-bridge

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object | `{}` |  |
| autoscaling.enabled | bool | `false` |  |
| autoscaling.maxReplicas | int | `100` |  |
| autoscaling.minReplicas | int | `1` |  |
| autoscaling.targetCPUUtilizationPercentage | int | `80` |  |
| config.lit_client_id | string | `""` | Client ID credentials for LIT API |
| config.lit_client_password | string | `""` | Password credentials for LIT API |
| config.lit_client_secret | string | `""` | Client Secret credentials for LIT API |
| config.lit_client_security_token | string | `""` | Security token credentials for LIT API |
| config.lit_client_username | string | `""` | Username credentials for LIT API |
| config.lit_domain | string | `""` | Domain for LIT API |
| config.lit_login_url | string | `""` | Login URL for LIT API |
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
| image.repository | string | `"374050862540.dkr.ecr.us-east-1.amazonaws.com/lit-bridge"` |  |
| image.tag | string | `""` |  |
| nodeSelector | object | `{}` |  |
| replicaCount | int | `1` | Number of lit-bridge pods to do calls to LIT API. |
| resources.limits.cpu | string | `"200m"` |  |
| resources.limits.memory | string | `"256Mi"` |  |
| resources.requests.cpu | string | `"100m"` |  |
| resources.requests.memory | string | `"128Mi"` |  |
| service.port | int | `5000` |  |
| service.type | string | `"ClusterIP"` |  |
| tolerations | list | `[]` |  |


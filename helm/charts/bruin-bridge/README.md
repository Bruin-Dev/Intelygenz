# bruin-bridge

![Version: 0.1.0](https://img.shields.io/badge/Version-0.1.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 1.16.0](https://img.shields.io/badge/AppVersion-1.16.0-informational?style=flat-square)

A Helm chart for Kubernetes to deploy microservice bruin-bridge

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object | `{}` |  |
| autoscaling.enabled | bool | `false` |  |
| autoscaling.maxReplicas | int | `100` |  |
| autoscaling.minReplicas | int | `1` |  |
| autoscaling.targetCPUUtilizationPercentage | int | `80` |  |
| config.bruin_base_url | string | `""` | Base URL for Bruin API |
| config.bruin_base_url_ip | string | `""` | Base URL for Bruin API (needed only in dev environments) |
| config.bruin_client_id | string | `""` | Client ID credentials for Bruin API |
| config.bruin_client_secret | string | `""` | Client Secret credentials for Bruin API |
| config.bruin_login_url | string | `""` | Login URL for Bruin API |
| config.bruin_login_url_ip | string | `""` | IP of Bruin Login URL (needed only in dev environments) |
| config.ecr_registry.name | string | `"ecr-registry"` | Name of the imagePullSecret created to access the images stored in ECR. |
| config.environment | string | `"dev"` | Name of environment for EKS cluster and network resources |
| config.environment_name | string | `"automation-test"` | Name of ephemeral environment for helm charts and redis elasticaches used |
| config.mode | string | `"aws"` | Indicates if the helm chart will be displayed in an aws or local environment, in case it is local, a specific imagePullSecret will be used to access the images stored in ECR. |
| config.nats_server | string | `"nats://nats:4222"` | NATS cluster endpoint used by bruin-bridge |
| config.papertrail_active | string | `"False"` | Indicates if the logs will be sent to papertrail or not. |
| config.papertrail_host | string | `"logs.papertrailapp.com"` | Papertrail host to which the logs will be sent |
| config.papertrail_port | string | `"0"` | Papertrail port to which the logs will be sent |
| config.redis_hostname | string | `"redis"` | Redis Hostname used to store heavy NATS messages (>1MB) |
| image.pullPolicy | string | `"IfNotPresent"` |  |
| image.repository | string | `"374050862540.dkr.ecr.us-east-1.amazonaws.com/automation-bruin-bridge"` |  |
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


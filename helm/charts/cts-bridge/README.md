# cts-bridge

![Version: 0.1.0](https://img.shields.io/badge/Version-0.1.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 1.16.0](https://img.shields.io/badge/AppVersion-1.16.0-informational?style=flat-square)

A Helm chart for Kubernetes to deploy microservice cts-bridge

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object | `{}` |  |
| autoscaling.enabled | bool | `false` |  |
| autoscaling.maxReplicas | int | `100` |  |
| autoscaling.minReplicas | int | `1` |  |
| autoscaling.targetCPUUtilizationPercentage | int | `80` |  |
| config.cts_client_id | string | `""` | Client ID credentials for CTS API |
| config.cts_client_password | string | `""` | Password credentials for CTS API |
| config.cts_client_secret | string | `""` | Client Secret credentials for CTS API |
| config.cts_client_security_token | string | `""` | Security Token credentials for CTS API |
| config.cts_client_username | string | `""` | Username credentials for CTS API |
| config.cts_domain | string | `""` | Domain URL for CTS API |
| config.cts_login_url | string | `""` | Login URL for CTS API |
| config.ecr_registry.name | string | `"ecr-registry"` | Name of the imagePullSecret created to access the images stored in ECR. |
| config.environment | string | `"dev"` | Name of environment for EKS cluster and network resources |
| config.environment_name | string | `"automation-test"` | Name of ephemeral environment for helm charts and redis elasticaches used |
| config.mode | string | `"aws"` | Indicates if the helm chart will be displayed in an aws or local environment, in case it is local, a specific imagePullSecret will be used to access the images stored in ECR. The only valid values are aws or local |
| config.nats_server | string | `"nats://nats:4222"` | NATS cluster endpoint used by cts-bridge |
| config.papertrail_active | string | `"False"` | Indicates if the logs will be sent to papertrail or not. |
| config.papertrail_host | string | `"logs.papertrailapp.com"` | Papertrail host to which the logs will be sent |
| config.papertrail_port | string | `"0"` | Papertrail port to which the logs will be sent |
| config.redis_hostname | string | `"redis"` | Redis Hostname used to store heavy NATS messages (>1MB) |
| image.pullPolicy | string | `"IfNotPresent"` |  |
| image.repository | string | `"374050862540.dkr.ecr.us-east-1.amazonaws.com/automation-cts-bridge"` |  |
| image.tag | string | `""` |  |
| nodeSelector | object | `{}` |  |
| replicaCount | int | `1` | Number of cts-bridge pods to do calls to CTS API. |
| service.port | int | `5000` |  |
| service.type | string | `"ClusterIP"` |  |
| tolerations | list | `[]` |  |


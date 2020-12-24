# tnba-feedback

![Version: 0.1.0](https://img.shields.io/badge/Version-0.1.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 1.16.0](https://img.shields.io/badge/AppVersion-1.16.0-informational?style=flat-square)

A Helm chart for Kubernetes to deploy microservice tnba-feedback

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object | `{}` |  |
| autoscaling.enabled | bool | `false` |  |
| autoscaling.maxReplicas | int | `100` |  |
| autoscaling.minReplicas | int | `1` |  |
| autoscaling.targetCPUUtilizationPercentage | int | `80` |  |
| config.capabilities_replicas.bruin_bridge | string | `"2"` | Number of replicas of bruin-bridge. If it is higher than 0 an initContainer will be created in the tnba-feedback deployment that will wait until the bruin-bridge service responds correctly to healthcheck calls. |
| config.capabilities_replicas.cts_bridge | string | `"1"` | Number of replicas of cts-bridge. If it is higher than 0 an initContainer will be created in the tnba-feedback deployment that will wait until the cts-bridge service responds correctly to healthcheck calls. |
| config.capabilities_replicas.hawkeye_bridge | string | `"0"` | Number of replicas of hawkeye-bridge. If it is higher than 0 an initContainer will be created in the tnba-feedback deployment that will wait until the hawkeye-bridge service responds correctly to healthcheck calls. |
| config.capabilities_replicas.lit_bridge | string | `"1"` | Number of replicas of lit-bridge. If it is higher than 0 an initContainer will be created in the tnba-feedback deployment that will wait until the lit-bridge service responds correctly to healthcheck calls. |
| config.capabilities_replicas.notifier | string | `"1"` | Number of replicas of notifier. If it is higher than 0 an initContainer will be created in the tnba-feedback deployment that will wait until the notifier service responds correctly to healthcheck calls. |
| config.capabilities_replicas.t7_bridge | string | `"1"` | Number of replicas of t7-bridge. If it is higher than 0 an initContainer will be created in the tnba-feedback deployment that will wait until the t7-bridge service responds correctly to healthcheck calls. |
| config.capabilities_replicas.velocloud_bridge | string | `"2"` | Number of replicas of velocloud-bridge. If it is higher than 0 an initContainer will be created in the tnba-feedback deployment that will wait until the velocloud-bridge service responds correctly to healthcheck calls. |
| config.ecr_registry.name | string | `"ecr-registry"` | Name of the imagePullSecret created to access the images stored in ECR. |
| config.environment | string | `"dev"` | Name of environment for EKS cluster and network resources |
| config.environment_name | string | `"automation-test"` | Name of ephemeral environment for helm charts and redis elasticaches used |
| config.mode | string | `"aws"` | Indicates if the helm chart will be displayed in an aws or local environment, in case it is local, a specific imagePullSecret will be used to access the images stored in ECR. |
| config.nats_server | string | `"nats://nats:4222"` | NATS cluster endpoint used by tnba-feedback |
| config.papertrail_active | string | `"False"` | Indicates if the logs will be sent to papertrail or not. |
| config.papertrail_host | string | `"logs.papertrailapp.com"` | Papertrail host to which the logs will be sent |
| config.papertrail_port | string | `"0"` | Papertrail port to which the logs will be sent |
| config.redis_hostname | string | `"redis"` | Redis Hostname used to store heavy NATS messages (>1MB) |
| config.redis_tnba_feedback_hostname | string | `"redis"` | Redis Hostname used to store metrics obtained from tnba-feedback to train the ML model |
| image.pullPolicy | string | `"IfNotPresent"` |  |
| image.repository | string | `"374050862540.dkr.ecr.us-east-1.amazonaws.com/automation-tnba-feedback"` |  |
| image.tag | string | `""` |  |
| nodeSelector | object | `{}` |  |
| replicaCount | int | `1` | Number of tnba-feedback pods |
| service.port | int | `5000` |  |
| service.type | string | `"ClusterIP"` |  |
| tolerations | list | `[]` |  |


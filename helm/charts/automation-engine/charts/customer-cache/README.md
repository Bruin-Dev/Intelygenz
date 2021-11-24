# customer-cache

![Version: 0.1.0](https://img.shields.io/badge/Version-0.1.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 1.16.0](https://img.shields.io/badge/AppVersion-1.16.0-informational?style=flat-square)

A Helm chart for Kubernetes to deploy microservice customer-cache

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object | `{}` |  |
| autoscaling.enabled | bool | `false` |  |
| autoscaling.maxReplicas | int | `100` |  |
| autoscaling.minReplicas | int | `1` |  |
| autoscaling.targetCPUUtilizationPercentage | int | `80` |  |
| config.timezone | string | `""` | |
| config.velocloud_hosts | list\<string\> | `[]` | VeloCloud hosts whose edges will be stored to the cache |
| config.duplicate_inventories_recipient | string | `""` | E-mail address that will get e-mails with a relation of service numbers that have multiple Bruin inventories |
| config.refresh_job_interval | int | `0` | Defines how often the cache is refreshed |
| config.refresh_check_interval | int | `0` | Defines how often the next refresh flag is checked to decide if it's time to refresh the cache or not |
| config.blacklisted_edges | list\<object\> | `[]` | VeloCloud edges that should be ignored in the caching process |
| config.blacklisted_clients_with_pending_status | list\<int\> | `[]` | Client IDs whose edges have Pending management status that should be ignored in the caching process |
| config.whitelisted_management_statuses | list\<string\> | `[]` | Management statuses that should be considered in the caching process |
| config.capabilities_enabled.bruin_bridge | bool | `true` | Indicate is bruin-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the bruin-bridge service responds correctly to healthcheck calls. |
| config.capabilities_enabled.hawkeye_bridge | bool | `true` | Indicate is hawkeye-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the hawkeye-bridge service responds correctly to healthcheck calls. |
| config.capabilities_enabled.notifier | bool | `true` | Indicate is notifier is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the notifier service responds correctly to healthcheck calls. |
| config.capabilities_enabled.t7_bridge | bool | `true` | Indicate is t8-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the t7-bridge service responds correctly to healthcheck calls. |
| config.capabilities_enabled.velocloud_bridge | bool | `true` | Indicate is velocloud-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the velocloud-bridge service responds correctly to healthcheck calls. |
| enabled | bool | `true` |  |
| global | object | `{"current_environment":"dev","ecr_registry":{"name":"ecr-registry"},"environment":"automation-test","mode":"aws","nats_server":"nats://nats:4222","papertrail_active":"False","papertrail_host":"logs.papertrailapp.com","papertrail_port":"0","redis_customer_cache_hostname":"redis","redis_hostname":"redis"}` | Global configuration |
| global.current_environment | string | `"dev"` | Name of environment for EKS cluster and network resources |
| global.ecr_registry.name | string | `"ecr-registry"` | Name of the imagePullSecret created to access the images stored in ECR. |
| global.environment | string | `"automation-test"` | Name of environment for helm charts and redis elasticaches used |
| global.mode | string | `"aws"` | Indicates if the helm chart will be displayed in an aws or local environment, in case it is local, a specific imagePullSecret will be used to access the images stored in ECR. |
| global.nats_server | string | `"nats://nats:4222"` | NATS cluster endpoint used by bruin-bridge |
| global.papertrail_active | string | `"False"` | Indicates if the logs will be sent to papertrail or not. |
| global.papertrail_host | string | `"logs.papertrailapp.com"` | Papertrail host to which the logs will be sent |
| global.papertrail_port | string | `"0"` | Papertrail port to which the logs will be sent |
| global.redis_customer_cache_hostname | string | `"redis"` | Redis hostname used to store information used by customer-cache |
| global.redis_hostname | string | `"redis"` | Redis Hostname used to store heavy NATS messages (>1MB) |
| image.pullPolicy | string | `"IfNotPresent"` |  |
| image.repository | string | `"374050862540.dkr.ecr.us-east-1.amazonaws.com/customer-cache"` |  |
| image.tag | string | `""` |  |
| nodeSelector | object | `{}` |  |
| replicaCount | int | `1` |  |
| resources.limits.cpu | string | `"400m"` |  |
| resources.limits.memory | string | `"512Mi"` |  |
| resources.requests.cpu | string | `"200m"` |  |
| resources.requests.memory | string | `"256Mi"` |  |
| service.port | int | `5000` |  |
| service.type | string | `"ClusterIP"` |  |
| tolerations | list | `[]` |  |


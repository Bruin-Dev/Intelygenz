# lumin-billing-report

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
| config.billing_recipient | string | `""` | Email address to send lumin-billing-report |
| config.customer_name | string | `""` | Name of customer to generate lumin-billing-report |
| config.ecr_registry.name | string | `"ecr-registry"` | Name of the imagePullSecret created to access the images stored in ECR. |
| config.email_acc_pwd | string | `""` | Email account password |
| config.environment | string | `"dev"` | Name of environment for EKS cluster and network resources |
| config.environment_name | string | `"automation-test"` | Name of ephemeral environment for helm charts and redis elasticaches used |
| config.lumin_token | string | `""` | Token credentials for Lumin API |
| config.lumin_uri | string | `""` | URI of Lumin API |
| config.mode | string | `"aws"` | Indicates if the helm chart will be displayed in an aws or local environment, in case it is local, a specific imagePullSecret will be used to access the images stored in ECR. |
| config.nats_server | string | `"nats://nats:4222"` | NATS cluster endpoint used by last-contact-report |
| config.papertrail_active | string | `"False"` | Indicates if the logs will be sent to papertrail or not. |
| config.papertrail_host | string | `"logs.papertrailapp.com"` | Papertrail host to which the logs will be sent |
| config.papertrail_port | string | `"0"` | Papertrail port to which the logs will be sent |
| image.pullPolicy | string | `"IfNotPresent"` |  |
| image.repository | string | `"374050862540.dkr.ecr.us-east-1.amazonaws.com/automation-lumin-billing-report"` |  |
| image.tag | string | `""` |  |
| nodeSelector | object | `{}` |  |
| replicaCount | int | `1` |  |
| service.port | int | `5000` |  |
| service.type | string | `"ClusterIP"` |  |
| tolerations | list | `[]` |  |


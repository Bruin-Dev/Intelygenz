# automation-engine

![Version: 0.1.0](https://img.shields.io/badge/Version-0.1.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 1.16.0](https://img.shields.io/badge/AppVersion-1.16.0-informational?style=flat-square)

A Helm chart for Kubernetes to deploy automation-engine project

## Requirements

| Repository | Name | Version |
|------------|------|---------|
|  | bruin-bridge | *.*.* |
|  | customer-cache | *.*.* |
|  | digi-bridge | *.*.* |
|  | hawkeye-bridge | *.*.* |
|  | hawkeye-customer-cache | *.*.* |
|  | hawkeye-outage-monitor | *.*.* |
|  | last-contact-report | *.*.* |
|  | lumin-billing-report | *.*.* |
|  | notifier | *.*.* |
|  | service-outage-monitor-1 | *.*.* |
|  | service-outage-monitor-2 | *.*.* |
|  | service-outage-monitor-3 | *.*.* |
|  | service-outage-monitor-4 | *.*.* |
|  | service-outage-monitor-triage | *.*.* |
|  | t7-bridge | *.*.* |
|  | tnba-feedback | *.*.* |
|  | tnba-monitor | *.*.* |
|  | velocloud-bridge | *.*.* |
| https://nats-io.github.io/k8s/helm/charts/ | nats | 0.7.2 |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object | `{}` |  |
| autoscaling.enabled | bool | `false` |  |
| autoscaling.maxReplicas | int | `100` |  |
| autoscaling.minReplicas | int | `1` |  |
| autoscaling.targetCPUUtilizationPercentage | int | `80` |  |
| bruin-bridge | object | `{"config":{"bruin_base_url":"","bruin_base_url_ip":"","bruin_client_id":"","bruin_client_secret":"","bruin_login_url":"","bruin_login_url_ip":""},"enabled":true,"image":{"pullPolicy":"IfNotPresent","repository":"374050862540.dkr.ecr.us-east-1.amazonaws.com/bruin-bridge","tag":""},"replicaCount":2,"resources":{"limits":{"cpu":"200m","memory":"256Mi"},"requests":{"cpu":"100m","memory":"128Mi"}},"service":{"port":5000,"type":"ClusterIP"}}` | bruin-bridge subchart specific configuration |
| bruin-bridge.config.bruin_base_url | string | `""` | Base URL for Bruin API |
| bruin-bridge.config.bruin_base_url_ip | string | `""` | Base URL for Bruin API (needed only in dev environments) |
| bruin-bridge.config.bruin_client_id | string | `""` | Client ID credentials for Bruin API |
| bruin-bridge.config.bruin_client_secret | string | `""` | Client Secret credentials for Bruin API |
| bruin-bridge.config.bruin_login_url | string | `""` | Login URL for Bruin API |
| bruin-bridge.config.bruin_login_url_ip | string | `""` | IP of Bruin Login URL (needed only in dev environments) |
| bruin-bridge.enabled | bool | `true` | Field to indicate if the bruin-bridge module is going to be deployed |
| bruin-bridge.image.repository | string | `"374050862540.dkr.ecr.us-east-1.amazonaws.com/bruin-bridge"` | Repository image for bruin-bridge module |
| bruin-bridge.replicaCount | int | `2` | Number of bruin-bridge pods to do calls to Bruin API. Do not set this below 2 unless is going to deploy in dev or local environment. |
| bruin-bridge.service | object | `{"port":5000,"type":"ClusterIP"}` | Service Configuration |
| cts-bridge | object | `{"config":{"cts_client_id":"","cts_client_password":"","cts_client_secret":"","cts_client_security_token":"","cts_client_username":"","cts_domain":"","cts_login_url":""},"enabled":true,"image":{"pullPolicy":"IfNotPresent","repository":"374050862540.dkr.ecr.us-east-1.amazonaws.com/cts-bridge","tag":""},"replicaCount":1,"resources":{"limits":{"cpu":"200m","memory":"256Mi"},"requests":{"cpu":"100m","memory":"128Mi"}},"service":{"port":5000,"type":"ClusterIP"}}` | cts-bridge subchart specific configuration |
| cts-bridge.config.cts_client_id | string | `""` | Client ID credentials for CTS API |
| cts-bridge.config.cts_client_password | string | `""` | Password credentials for CTS API |
| cts-bridge.config.cts_client_secret | string | `""` | Client Secret credentials for CTS API |
| cts-bridge.config.cts_client_security_token | string | `""` | Security Token credentials for CTS API |
| cts-bridge.config.cts_client_username | string | `""` | Username credentials for CTS API |
| cts-bridge.config.cts_domain | string | `""` | Domain URL for CTS API |
| cts-bridge.config.cts_login_url | string | `""` | Login URL for CTS API |
| cts-bridge.enabled | bool | `true` | Field to indicate if the cts-bridge module is going to be deployed |
| cts-bridge.image | object | `{"pullPolicy":"IfNotPresent","repository":"374050862540.dkr.ecr.us-east-1.amazonaws.com/cts-bridge","tag":""}` | cts-bridge image details |
| cts-bridge.image.repository | string | `"374050862540.dkr.ecr.us-east-1.amazonaws.com/cts-bridge"` | cts-bridge |
| cts-bridge.image.tag | string | `""` | cts-bridge tag of docker image |
| cts-bridge.service | object | `{"port":5000,"type":"ClusterIP"}` | cts-bridge service details |
| customer-cache | object | `{"config":{"capabilities_enabled":{"bruin_bridge":true,"cts_bridge":true,"hawkeye_bridge":true,"lit_bridge":true,"notifier":true,"t7_bridge":true,"velocloud_bridge":true}},"enabled":true,"image":{"pullPolicy":"IfNotPresent","repository":"374050862540.dkr.ecr.us-east-1.amazonaws.com/customer-cache","tag":""},"replicaCount":1,"resources":{"limits":{"cpu":"400m","memory":"512Mi"},"requests":{"cpu":"200m","memory":"256Mi"}},"service":{"port":5000,"type":"ClusterIP"}}` | customer-cache subchart specific configuration |
| customer-cache.config.capabilities_enabled.bruin_bridge | bool | `true` | Indicate is bruin-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the bruin-bridge service responds correctly to healthcheck calls. |
| customer-cache.config.capabilities_enabled.cts_bridge | bool | `true` | Indicate is cts-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the cts-bridge service responds correctly to healthcheck calls. |
| customer-cache.config.capabilities_enabled.hawkeye_bridge | bool | `true` | Indicate is hawkeye-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the hawkeye-bridge service responds correctly to healthcheck calls. |
| customer-cache.config.capabilities_enabled.lit_bridge | bool | `true` | Indicate is lit-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the lit-bridge service responds correctly to healthcheck calls. |
| customer-cache.config.capabilities_enabled.notifier | bool | `true` | Indicate is notifier is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the notifier service responds correctly to healthcheck calls. |
| customer-cache.config.capabilities_enabled.t7_bridge | bool | `true` | Indicate is t8-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the t7-bridge service responds correctly to healthcheck calls. |
| customer-cache.config.capabilities_enabled.velocloud_bridge | bool | `true` | Indicate is velocloud-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the velocloud-bridge service responds correctly to healthcheck calls. |
| digi-bridge | object | `{"config":{"digi_base_url":"","digi_client_id":"","digi_client_secret":"","digi_ip_dev":"","digi_ip_pro":"","digi_ip_test":"","digi_record_name_dev":"","digi_record_name_pro":"","digi_record_name_test":""},"enabled":true,"image":{"pullPolicy":"IfNotPresent","repository":"374050862540.dkr.ecr.us-east-1.amazonaws.com/digi-bridge","tag":""},"replicaCount":1,"resources":{"limits":{"cpu":"200m","memory":"256Mi"},"requests":{"cpu":"100m","memory":"128Mi"}},"service":{"port":5000,"type":"ClusterIP"}}` | digi-bridge subchart specific configuration |
| digi-bridge.config.digi_base_url | string | `""` | Base URL for Digi API |
| digi-bridge.config.digi_client_id | string | `""` | Client ID credentials for Digi API |
| digi-bridge.config.digi_client_secret | string | `""` | Client Secret credentials for Digi API |
| digi-bridge.config.digi_ip_dev | string | `""` | IP for Digi Dev Environment |
| digi-bridge.config.digi_ip_pro | string | `""` | IP for Digi Production Environment |
| digi-bridge.config.digi_ip_test | string | `""` | IP for Digi Test Environment |
| digi-bridge.config.digi_record_name_dev | string | `""` | Record name for Digi Dev Environment |
| digi-bridge.config.digi_record_name_pro | string | `""` | Record name for Digi Production Environment |
| digi-bridge.config.digi_record_name_test | string | `""` | Record name for Digi Test Environment |
| digi-bridge.enabled | bool | `true` | Field to indicate if the digi-bridge module is going to be deployed |
| dispatch-portal-backend.config.capabilities_enabled.bruin_bridge | bool | `true` | Indicate is bruin-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the bruin-bridge service responds correctly to healthcheck calls. |
| dispatch-portal-backend.config.capabilities_enabled.cts_bridge | bool | `true` | Indicate is cts-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the cts-bridge service responds correctly to healthcheck calls. |
| dispatch-portal-backend.config.capabilities_enabled.hawkeye_bridge | bool | `true` | Indicate is hawkeye-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the hawkeye-bridge service responds correctly to healthcheck calls. |
| dispatch-portal-backend.config.capabilities_enabled.lit_bridge | bool | `true` | Indicate is lit-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the lit-bridge service responds correctly to healthcheck calls. |
| dispatch-portal-backend.config.capabilities_enabled.notifier | bool | `true` | Indicate is notifier is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the notifier service responds correctly to healthcheck calls. |
| dispatch-portal-backend.config.capabilities_enabled.t7_bridge | bool | `true` | Indicate is t8-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the t7-bridge service responds correctly to healthcheck calls. |
| dispatch-portal-backend.config.capabilities_enabled.velocloud_bridge | bool | `true` | Indicate is velocloud-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the velocloud-bridge service responds correctly to healthcheck calls. |
| dispatch-portal-backend.config.dispatch_portal_server_port | int | `5000` |  |
| dispatch-portal-backend.enabled | bool | `true` |  |
| dispatch-portal-backend.image.pullPolicy | string | `"IfNotPresent"` |  |
| dispatch-portal-backend.image.repository | string | `"374050862540.dkr.ecr.us-east-1.amazonaws.com/dispatch-portal-backend"` |  |
| dispatch-portal-backend.image.tag | string | `""` |  |
| dispatch-portal-backend.replicaCount | int | `1` |  |
| dispatch-portal-backend.resources.limits.cpu | string | `"200m"` |  |
| dispatch-portal-backend.resources.limits.memory | string | `"256Mi"` |  |
| dispatch-portal-backend.resources.requests.cpu | string | `"100m"` |  |
| dispatch-portal-backend.resources.requests.memory | string | `"128Mi"` |  |
| dispatch-portal-backend.service.port | int | `5000` |  |
| dispatch-portal-backend.service.type | string | `"ClusterIP"` |  |
| dispatch-portal-frontend.enabled | bool | `true` |  |
| dispatch-portal-frontend.image.pullPolicy | string | `"IfNotPresent"` |  |
| dispatch-portal-frontend.image.repository | string | `"374050862540.dkr.ecr.us-east-1.amazonaws.com/dispatch-portal-frontend"` |  |
| dispatch-portal-frontend.image.tag | string | `""` |  |
| dispatch-portal-frontend.replicaCount | int | `1` |  |
| dispatch-portal-frontend.resources.limits.cpu | string | `"200m"` |  |
| dispatch-portal-frontend.resources.limits.memory | string | `"256Mi"` |  |
| dispatch-portal-frontend.resources.requests.cpu | string | `"100m"` |  |
| dispatch-portal-frontend.resources.requests.memory | string | `"128Mi"` |  |
| dispatch-portal-frontend.service.port | int | `3000` |  |
| dispatch-portal-frontend.service.type | string | `"ClusterIP"` |  |
| global | object | `{"current_environment":"dev","ecr_registry":{"name":"ecr-registry"},"email_acc_pwd":"","environment":"automation-test","last_contact_recipient":"","mode":"aws","nats_server":"nats://nats:4222","papertrail_active":"False","papertrail_host":"logs.papertrailapp.com","papertrail_port":"0","redis_customer_cache_hostname":"redis","redis_hostname":"redis","redis_tnba_feedback_hostname":"redis"}` | Global configuration for all subcharts |
| global.current_environment | string | `"dev"` | Name of environment for EKS cluster and network resources |
| global.ecr_registry.name | string | `"ecr-registry"` | Name of the imagePullSecret created to access the images stored in ECR. |
| global.email_acc_pwd | string | `""` | Email account password |
| global.environment | string | `"automation-test"` | Name of environment for helm charts and redis elasticaches used |
| global.mode | string | `"aws"` | Indicates if the helm chart will be displayed in an aws or local environment, in case it is local, a specific imagePullSecret will be used to access the images stored in ECR. |
| global.nats_server | string | `"nats://nats:4222"` | NATS cluster endpoint used by bruin-bridge |
| global.papertrail_active | string | `"False"` | Indicates if the logs will be sent to papertrail or not. |
| global.papertrail_host | string | `"logs.papertrailapp.com"` | Papertrail host to which the logs will be sent |
| global.papertrail_port | string | `"0"` | Papertrail port to which the logs will be sent |
| global.redis_customer_cache_hostname | string | `"redis"` | Redis hostname used to store information used by customer-cache |
| global.redis_hostname | string | `"redis"` | Redis Hostname used to store heavy NATS messages (>1MB) |
| global.redis_tnba_feedback_hostname | string | `"redis"` | Redis Hostname used to store metrics obtained from tnba-feedback to train the ML model |
| hawkeye-bridge | object | `{"config":{"hawkeye_base_url":"","hawkeye_client_password":"","hawkeye_client_username":""},"enabled":true,"image":{"pullPolicy":"IfNotPresent","repository":"374050862540.dkr.ecr.us-east-1.amazonaws.com/hawkeye-bridge","tag":""},"replicaCount":1,"resources":{"limits":{"cpu":"200m","memory":"256Mi"},"requests":{"cpu":"100m","memory":"128Mi"}},"service":{"port":5000,"type":"ClusterIP"}}` | hawkeye-bridge subchart specific configuration |
| hawkeye-bridge.config.hawkeye_client_password | string | `""` | Client password credentials for Hawkeye API |
| hawkeye-customer-cache.config.capabilities_enabled.bruin_bridge | bool | `true` | Indicate is bruin-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the bruin-bridge service responds correctly to healthcheck calls. |
| hawkeye-customer-cache.config.capabilities_enabled.cts_bridge | bool | `true` | Indicate is cts-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the cts-bridge service responds correctly to healthcheck calls. |
| hawkeye-customer-cache.config.capabilities_enabled.hawkeye_bridge | bool | `true` | Indicate is hawkeye-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the hawkeye-bridge service responds correctly to healthcheck calls. |
| hawkeye-customer-cache.config.capabilities_enabled.lit_bridge | bool | `true` | Indicate is lit-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the lit-bridge service responds correctly to healthcheck calls. |
| hawkeye-customer-cache.config.capabilities_enabled.notifier | bool | `true` | Indicate is notifier is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the notifier service responds correctly to healthcheck calls. |
| hawkeye-customer-cache.config.capabilities_enabled.t7_bridge | bool | `true` | Indicate is t8-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the t7-bridge service responds correctly to healthcheck calls. |
| hawkeye-customer-cache.config.capabilities_enabled.velocloud_bridge | bool | `true` | Indicate is velocloud-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the velocloud-bridge service responds correctly to healthcheck calls. |
| hawkeye-customer-cache.enabled | bool | `true` |  |
| hawkeye-customer-cache.image.pullPolicy | string | `"IfNotPresent"` |  |
| hawkeye-customer-cache.image.repository | string | `"374050862540.dkr.ecr.us-east-1.amazonaws.com/hawkeye-customer-cache"` |  |
| hawkeye-customer-cache.image.tag | string | `""` |  |
| hawkeye-customer-cache.replicaCount | int | `1` |  |
| hawkeye-customer-cache.resources.limits.cpu | string | `"400m"` |  |
| hawkeye-customer-cache.resources.limits.memory | string | `"512Mi"` |  |
| hawkeye-customer-cache.resources.requests.cpu | string | `"200m"` |  |
| hawkeye-customer-cache.resources.requests.memory | string | `"256Mi"` |  |
| hawkeye-customer-cache.service.port | int | `5000` |  |
| hawkeye-customer-cache.service.type | string | `"ClusterIP"` |  |
| hawkeye-outage-monitor.config.capabilities_enabled.bruin_bridge | bool | `true` | Indicate is bruin-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the bruin-bridge service responds correctly to healthcheck calls. |
| hawkeye-outage-monitor.config.capabilities_enabled.cts_bridge | bool | `true` | Indicate is cts-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the cts-bridge service responds correctly to healthcheck calls. |
| hawkeye-outage-monitor.config.capabilities_enabled.hawkeye_bridge | bool | `true` | Indicate is hawkeye-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the hawkeye-bridge service responds correctly to healthcheck calls. |
| hawkeye-outage-monitor.config.capabilities_enabled.lit_bridge | bool | `true` | Indicate is lit-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the lit-bridge service responds correctly to healthcheck calls. |
| hawkeye-outage-monitor.config.capabilities_enabled.notifier | bool | `true` | Indicate is notifier is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the notifier service responds correctly to healthcheck calls. |
| hawkeye-outage-monitor.config.capabilities_enabled.t7_bridge | bool | `true` | Indicate is t8-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the t7-bridge service responds correctly to healthcheck calls. |
| hawkeye-outage-monitor.config.capabilities_enabled.velocloud_bridge | bool | `true` | Indicate is velocloud-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the velocloud-bridge service responds correctly to healthcheck calls. |
| hawkeye-outage-monitor.enabled | bool | `true` |  |
| hawkeye-outage-monitor.image.pullPolicy | string | `"IfNotPresent"` |  |
| hawkeye-outage-monitor.image.repository | string | `"374050862540.dkr.ecr.us-east-1.amazonaws.com/hawkeye-outage-monitor"` |  |
| hawkeye-outage-monitor.image.tag | string | `""` |  |
| hawkeye-outage-monitor.replicaCount | int | `1` |  |
| hawkeye-outage-monitor.resources.limits.cpu | string | `"200m"` |  |
| hawkeye-outage-monitor.resources.limits.memory | string | `"256Mi"` |  |
| hawkeye-outage-monitor.resources.requests.cpu | string | `"100m"` |  |
| hawkeye-outage-monitor.resources.requests.memory | string | `"128Mi"` |  |
| hawkeye-outage-monitor.service.port | int | `5000` |  |
| hawkeye-outage-monitor.service.type | string | `"ClusterIP"` |  |
| last-contact-report.config.capabilities_enabled.bruin_bridge | bool | `true` | Indicate is bruin-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the bruin-bridge service responds correctly to healthcheck calls. |
| last-contact-report.config.capabilities_enabled.cts_bridge | bool | `true` | Indicate is cts-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the cts-bridge service responds correctly to healthcheck calls. |
| last-contact-report.config.capabilities_enabled.hawkeye_bridge | bool | `true` | Indicate is hawkeye-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the hawkeye-bridge service responds correctly to healthcheck calls. |
| last-contact-report.config.capabilities_enabled.lit_bridge | bool | `true` | Indicate is lit-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the lit-bridge service responds correctly to healthcheck calls. |
| last-contact-report.config.capabilities_enabled.notifier | bool | `true` | Indicate is notifier is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the notifier service responds correctly to healthcheck calls. |
| last-contact-report.config.capabilities_enabled.t7_bridge | bool | `true` | Indicate is t8-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the t7-bridge service responds correctly to healthcheck calls. |
| last-contact-report.config.capabilities_enabled.velocloud_bridge | bool | `true` | Indicate is velocloud-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the velocloud-bridge service responds correctly to healthcheck calls. |
| last-contact-report.enabled | bool | `true` |  |
| last-contact-report.image.pullPolicy | string | `"IfNotPresent"` |  |
| last-contact-report.image.repository | string | `"374050862540.dkr.ecr.us-east-1.amazonaws.com/last-contact-report"` |  |
| last-contact-report.image.tag | string | `""` |  |
| last-contact-report.replicaCount | int | `1` |  |
| last-contact-report.resources.limits.cpu | string | `"200m"` |  |
| last-contact-report.resources.limits.memory | string | `"256Mi"` |  |
| last-contact-report.resources.requests.cpu | string | `"100m"` |  |
| last-contact-report.resources.requests.memory | string | `"128Mi"` |  |
| last-contact-report.service.port | int | `5000` |  |
| last-contact-report.service.type | string | `"ClusterIP"` |  |
| lit-bridge | object | `{"config":{"lit_client_id":"","lit_client_password":"","lit_client_secret":"","lit_client_security_token":"","lit_client_username":"","lit_domain":"","lit_login_url":""},"enabled":true,"global":{"current_environment":"dev","ecr_registry":{"name":"ecr-registry"},"environment":"automation-test","mode":"aws","nats_server":"nats://nats:4222","papertrail_active":"False","papertrail_host":"logs.papertrailapp.com","papertrail_port":"0","redis_hostname":"redis"},"image":{"pullPolicy":"IfNotPresent","repository":"374050862540.dkr.ecr.us-east-1.amazonaws.com/lit-bridge","tag":""},"replicaCount":1,"resources":{"limits":{"cpu":"200m","memory":"256Mi"},"requests":{"cpu":"100m","memory":"128Mi"}},"service":{"port":5000,"type":"ClusterIP"}}` | lit-bridge subchart specific configuration |
| lit-bridge.config.lit_client_id | string | `""` | Client ID credentials for LIT API |
| lit-bridge.config.lit_client_password | string | `""` | Password credentials for LIT API |
| lit-bridge.config.lit_client_secret | string | `""` | Client Secret credentials for LIT API |
| lit-bridge.config.lit_client_security_token | string | `""` | Security token credentials for LIT API |
| lit-bridge.config.lit_client_username | string | `""` | Username credentials for LIT API |
| lit-bridge.config.lit_domain | string | `""` | Domain for LIT API |
| lit-bridge.config.lit_login_url | string | `""` | Login URL for LIT API |
| lit-bridge.global | object | `{"current_environment":"dev","ecr_registry":{"name":"ecr-registry"},"environment":"automation-test","mode":"aws","nats_server":"nats://nats:4222","papertrail_active":"False","papertrail_host":"logs.papertrailapp.com","papertrail_port":"0","redis_hostname":"redis"}` | Global configuration |
| lit-bridge.global.current_environment | string | `"dev"` | Name of environment for EKS cluster and network resources |
| lit-bridge.global.ecr_registry.name | string | `"ecr-registry"` | Name of the imagePullSecret created to access the images stored in ECR. |
| lit-bridge.global.environment | string | `"automation-test"` | Name of environment for helm charts and redis elasticaches used |
| lit-bridge.global.mode | string | `"aws"` | Indicates if the helm chart will be displayed in an aws or local environment, in case it is local, a specific imagePullSecret will be used to access the images stored in ECR. |
| lit-bridge.global.nats_server | string | `"nats://nats:4222"` | NATS cluster endpoint used by bruin-bridge |
| lit-bridge.global.papertrail_active | string | `"False"` | Indicates if the logs will be sent to papertrail or not. |
| lit-bridge.global.papertrail_host | string | `"logs.papertrailapp.com"` | Papertrail host to which the logs will be sent |
| lit-bridge.global.papertrail_port | string | `"0"` | Papertrail port to which the logs will be sent |
| lit-bridge.global.redis_hostname | string | `"redis"` | Redis Hostname used to store heavy NATS messages (>1MB) |
| lit-bridge.replicaCount | int | `1` | Number of lit-bridge pods to do calls to LIT API. |
| lumin-billing-report.autoscaling.enabled | bool | `false` |  |
| lumin-billing-report.autoscaling.maxReplicas | int | `100` |  |
| lumin-billing-report.autoscaling.minReplicas | int | `1` |  |
| lumin-billing-report.autoscaling.targetCPUUtilizationPercentage | int | `80` |  |
| lumin-billing-report.config.billing_recipient | string | `""` | Email address to send lumin-billing-report |
| lumin-billing-report.config.customer_name | string | `""` | Name of customer to generate lumin-billing-report |
| lumin-billing-report.config.lumin_token | string | `""` | Token credentials for Lumin API |
| lumin-billing-report.config.lumin_uri | string | `""` | URI of Lumin API |
| lumin-billing-report.enabled | bool | `true` |  |
| lumin-billing-report.image.pullPolicy | string | `"IfNotPresent"` |  |
| lumin-billing-report.image.repository | string | `"374050862540.dkr.ecr.us-east-1.amazonaws.com/lumin-billing-report"` |  |
| lumin-billing-report.image.tag | string | `""` |  |
| lumin-billing-report.replicaCount | int | `1` |  |
| lumin-billing-report.resources.limits.cpu | string | `"200m"` |  |
| lumin-billing-report.resources.limits.memory | string | `"256Mi"` |  |
| lumin-billing-report.resources.requests.cpu | string | `"100m"` |  |
| lumin-billing-report.resources.requests.memory | string | `"128Mi"` |  |
| lumin-billing-report.service.port | int | `5000` |  |
| lumin-billing-report.service.type | string | `"ClusterIP"` |  |
| nats | object | `{"cluster":{"enabled":true},"nameOverride":"nats","natsbox":{"enabled":false}}` | nats helm chart configuration |
| nats.nameOverride | string | `"nats"` | override name to use nats as name for svc, deployment and all created by nats helm chart |
| nodeSelector | object | `{}` |  |
| notifier | object | `{"config":{"slack_url":"","telestax_account_sid":"","telestax_auth_token":"","telestax_from_phone_number":"","telestax_url":""},"enabled":true,"image":{"pullPolicy":"IfNotPresent","repository":"374050862540.dkr.ecr.us-east-1.amazonaws.com/notifier","tag":""},"replicaCount":1,"resources":{"limits":{"cpu":"200m","memory":"256Mi"},"requests":{"cpu":"100m","memory":"128Mi"}},"service":{"port":5000,"type":"ClusterIP"}}` | notifier subchart specific configuration |
| notifier.config.slack_url | string | `""` | Slack Webhook URL to send messages |
| notifier.config.telestax_account_sid | string | `""` | Telestax account SID |
| notifier.config.telestax_auth_token | string | `""` | Telestax auth token credentials |
| notifier.config.telestax_url | string | `""` | Telestax URL |
| notifier.enabled | bool | `true` | Field to indicate if the notifier module is going to be deployed |
| notifier.image | object | `{"pullPolicy":"IfNotPresent","repository":"374050862540.dkr.ecr.us-east-1.amazonaws.com/notifier","tag":""}` | notifier image details |
| notifier.image.repository | string | `"374050862540.dkr.ecr.us-east-1.amazonaws.com/notifier"` | notifier repository for docker images |
| notifier.image.tag | string | `""` | notifier tag of docker image |
| notifier.service | object | `{"port":5000,"type":"ClusterIP"}` | notifier Service Configuration |
| replicaCount | int | `1` | Number of bruin-bridge pods to do calls to Bruin API. Do not set this below 2 unless is going to deploy in dev or local environment. |
| service-affecting-monitor.config.capabilities_enabled.bruin_bridge | bool | `true` | Indicate is bruin-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the bruin-bridge service responds correctly to healthcheck calls. |
| service-affecting-monitor.config.capabilities_enabled.cts_bridge | bool | `true` | Indicate is cts-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the cts-bridge service responds correctly to healthcheck calls. |
| service-affecting-monitor.config.capabilities_enabled.hawkeye_bridge | bool | `true` | Indicate is hawkeye-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the hawkeye-bridge service responds correctly to healthcheck calls. |
| service-affecting-monitor.config.capabilities_enabled.lit_bridge | bool | `true` | Indicate is lit-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the lit-bridge service responds correctly to healthcheck calls. |
| service-affecting-monitor.config.capabilities_enabled.notifier | bool | `true` | Indicate is notifier is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the notifier service responds correctly to healthcheck calls. |
| service-affecting-monitor.config.capabilities_enabled.t7_bridge | bool | `true` | Indicate is t8-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the t7-bridge service responds correctly to healthcheck calls. |
| service-affecting-monitor.config.capabilities_enabled.velocloud_bridge | bool | `true` | Indicate is velocloud-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the velocloud-bridge service responds correctly to healthcheck calls. |
| service-affecting-monitor.enabled | bool | `true` |  |
| service-affecting-monitor.image.pullPolicy | string | `"IfNotPresent"` |  |
| service-affecting-monitor.image.repository | string | `"374050862540.dkr.ecr.us-east-1.amazonaws.com/service-affecting-monitor"` |  |
| service-affecting-monitor.image.tag | string | `""` |  |
| service-affecting-monitor.replicaCount | int | `1` |  |
| service-affecting-monitor.resources.limits.cpu | string | `"200m"` |  |
| service-affecting-monitor.resources.limits.memory | string | `"256Mi"` |  |
| service-affecting-monitor.resources.requests.cpu | string | `"100m"` |  |
| service-affecting-monitor.resources.requests.memory | string | `"128Mi"` |  |
| service-affecting-monitor.service.port | int | `5000` |  |
| service-affecting-monitor.service.type | string | `"ClusterIP"` |  |
| service-dispatch-monitor.config.capabilities_enabled.bruin_bridge | bool | `true` | Indicate is bruin-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the bruin-bridge service responds correctly to healthcheck calls. |
| service-dispatch-monitor.config.capabilities_enabled.cts_bridge | bool | `true` | Indicate is cts-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the cts-bridge service responds correctly to healthcheck calls. |
| service-dispatch-monitor.config.capabilities_enabled.hawkeye_bridge | bool | `true` | Indicate is hawkeye-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the hawkeye-bridge service responds correctly to healthcheck calls. |
| service-dispatch-monitor.config.capabilities_enabled.lit_bridge | bool | `true` | Indicate is lit-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the lit-bridge service responds correctly to healthcheck calls. |
| service-dispatch-monitor.config.capabilities_enabled.notifier | bool | `true` | Indicate is notifier is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the notifier service responds correctly to healthcheck calls. |
| service-dispatch-monitor.config.capabilities_enabled.t7_bridge | bool | `true` | Indicate is t8-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the t7-bridge service responds correctly to healthcheck calls. |
| service-dispatch-monitor.config.capabilities_enabled.velocloud_bridge | bool | `true` | Indicate is velocloud-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the velocloud-bridge service responds correctly to healthcheck calls. |
| service-dispatch-monitor.enabled | bool | `true` |  |
| service-dispatch-monitor.image.pullPolicy | string | `"IfNotPresent"` |  |
| service-dispatch-monitor.image.repository | string | `"374050862540.dkr.ecr.us-east-1.amazonaws.com/service-dispatch-monitor"` |  |
| service-dispatch-monitor.image.tag | string | `""` |  |
| service-dispatch-monitor.replicaCount | int | `1` |  |
| service-dispatch-monitor.resources.limits.cpu | string | `"200m"` |  |
| service-dispatch-monitor.resources.limits.memory | string | `"256Mi"` |  |
| service-dispatch-monitor.resources.requests.cpu | string | `"100m"` |  |
| service-dispatch-monitor.resources.requests.memory | string | `"128Mi"` |  |
| service-dispatch-monitor.service.port | int | `5000` |  |
| service-dispatch-monitor.service.type | string | `"ClusterIP"` |  |
| service-outage-monitor-1.config.capabilities_enabled.bruin_bridge | bool | `true` | Indicate is bruin-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the bruin-bridge service responds correctly to healthcheck calls. |
| service-outage-monitor-1.config.capabilities_enabled.cts_bridge | bool | `true` | Indicate is cts-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the cts-bridge service responds correctly to healthcheck calls. |
| service-outage-monitor-1.config.capabilities_enabled.hawkeye_bridge | bool | `true` | Indicate is hawkeye-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the hawkeye-bridge service responds correctly to healthcheck calls. |
| service-outage-monitor-1.config.capabilities_enabled.lit_bridge | bool | `true` | Indicate is lit-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the lit-bridge service responds correctly to healthcheck calls. |
| service-outage-monitor-1.config.capabilities_enabled.notifier | bool | `true` | Indicate is notifier is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the notifier service responds correctly to healthcheck calls. |
| service-outage-monitor-1.config.capabilities_enabled.t7_bridge | bool | `true` | Indicate is t8-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the t7-bridge service responds correctly to healthcheck calls. |
| service-outage-monitor-1.config.capabilities_enabled.velocloud_bridge | bool | `true` | Indicate is velocloud-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the velocloud-bridge service responds correctly to healthcheck calls. |
| service-outage-monitor-1.config.enable_triage_monitoring | string | `"0"` |  |
| service-outage-monitor-1.config.velocloud_hosts | string | `"host1"` | Velocloud hosts |
| service-outage-monitor-1.config.velocloud_hosts_filter | string | `"host1_filter"` | Filter for Velocloud hosts |
| service-outage-monitor-1.enabled | bool | `true` |  |
| service-outage-monitor-1.image.pullPolicy | string | `"IfNotPresent"` |  |
| service-outage-monitor-1.image.repository | string | `"374050862540.dkr.ecr.us-east-1.amazonaws.com/service-outage-monitor"` |  |
| service-outage-monitor-1.image.tag | string | `""` |  |
| service-outage-monitor-1.replicaCount | int | `1` |  |
| service-outage-monitor-1.resources.limits.cpu | string | `"200m"` |  |
| service-outage-monitor-1.resources.limits.memory | string | `"256Mi"` |  |
| service-outage-monitor-1.resources.requests.cpu | string | `"100m"` |  |
| service-outage-monitor-1.resources.requests.memory | string | `"128Mi"` |  |
| service-outage-monitor-1.service.port | int | `5000` |  |
| service-outage-monitor-1.service.type | string | `"ClusterIP"` |  |
| service-outage-monitor-2.config.capabilities_enabled.bruin_bridge | bool | `true` | Indicate is bruin-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the bruin-bridge service responds correctly to healthcheck calls. |
| service-outage-monitor-2.config.capabilities_enabled.cts_bridge | bool | `true` | Indicate is cts-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the cts-bridge service responds correctly to healthcheck calls. |
| service-outage-monitor-2.config.capabilities_enabled.hawkeye_bridge | bool | `true` | Indicate is hawkeye-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the hawkeye-bridge service responds correctly to healthcheck calls. |
| service-outage-monitor-2.config.capabilities_enabled.lit_bridge | bool | `true` | Indicate is lit-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the lit-bridge service responds correctly to healthcheck calls. |
| service-outage-monitor-2.config.capabilities_enabled.notifier | bool | `true` | Indicate is notifier is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the notifier service responds correctly to healthcheck calls. |
| service-outage-monitor-2.config.capabilities_enabled.t7_bridge | bool | `true` | Indicate is t8-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the t7-bridge service responds correctly to healthcheck calls. |
| service-outage-monitor-2.config.capabilities_enabled.velocloud_bridge | bool | `true` | Indicate is velocloud-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the velocloud-bridge service responds correctly to healthcheck calls. |
| service-outage-monitor-2.config.enable_triage_monitoring | string | `"0"` |  |
| service-outage-monitor-2.config.velocloud_hosts | string | `"host2"` | Velocloud hosts |
| service-outage-monitor-2.config.velocloud_hosts_filter | string | `"host2_filter"` | Filter for Velocloud hosts |
| service-outage-monitor-2.enabled | bool | `true` |  |
| service-outage-monitor-2.image.pullPolicy | string | `"IfNotPresent"` |  |
| service-outage-monitor-2.image.repository | string | `"374050862540.dkr.ecr.us-east-1.amazonaws.com/service-outage-monitor"` |  |
| service-outage-monitor-2.image.tag | string | `""` |  |
| service-outage-monitor-2.replicaCount | int | `1` |  |
| service-outage-monitor-2.resources.limits.cpu | string | `"200m"` |  |
| service-outage-monitor-2.resources.limits.memory | string | `"256Mi"` |  |
| service-outage-monitor-2.resources.requests.cpu | string | `"100m"` |  |
| service-outage-monitor-2.resources.requests.memory | string | `"128Mi"` |  |
| service-outage-monitor-2.service.port | int | `5000` |  |
| service-outage-monitor-2.service.type | string | `"ClusterIP"` |  |
| service-outage-monitor-3.config.capabilities_enabled.bruin_bridge | bool | `true` | Indicate is bruin-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the bruin-bridge service responds correctly to healthcheck calls. |
| service-outage-monitor-3.config.capabilities_enabled.cts_bridge | bool | `true` | Indicate is cts-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the cts-bridge service responds correctly to healthcheck calls. |
| service-outage-monitor-3.config.capabilities_enabled.hawkeye_bridge | bool | `true` | Indicate is hawkeye-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the hawkeye-bridge service responds correctly to healthcheck calls. |
| service-outage-monitor-3.config.capabilities_enabled.lit_bridge | bool | `true` | Indicate is lit-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the lit-bridge service responds correctly to healthcheck calls. |
| service-outage-monitor-3.config.capabilities_enabled.notifier | bool | `true` | Indicate is notifier is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the notifier service responds correctly to healthcheck calls. |
| service-outage-monitor-3.config.capabilities_enabled.t7_bridge | bool | `true` | Indicate is t8-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the t7-bridge service responds correctly to healthcheck calls. |
| service-outage-monitor-3.config.capabilities_enabled.velocloud_bridge | bool | `true` | Indicate is velocloud-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the velocloud-bridge service responds correctly to healthcheck calls. |
| service-outage-monitor-3.config.enable_triage_monitoring | string | `"0"` |  |
| service-outage-monitor-3.config.velocloud_hosts | string | `"host1"` | Velocloud hosts |
| service-outage-monitor-3.config.velocloud_hosts_filter | string | `"host1_filter"` | Filter for Velocloud hosts |
| service-outage-monitor-3.enabled | bool | `true` |  |
| service-outage-monitor-3.global | object | `{"current_environment":"dev","ecr_registry":{"name":"ecr-registry"},"environment":"automation-test","mode":"aws","nats_server":"nats://nats:4222","papertrail_active":"False","papertrail_host":"logs.papertrailapp.com","papertrail_port":"0","redis_hostname":"redis"}` | Global configuration |
| service-outage-monitor-3.global.current_environment | string | `"dev"` | Name of environment for EKS cluster and network resources |
| service-outage-monitor-3.global.ecr_registry.name | string | `"ecr-registry"` | Name of the imagePullSecret created to access the images stored in ECR. |
| service-outage-monitor-3.global.environment | string | `"automation-test"` | Name of environment for helm charts and redis elasticaches used |
| service-outage-monitor-3.global.mode | string | `"aws"` | Indicates if the helm chart will be displayed in an aws or local environment, in case it is local, a specific imagePullSecret will be used to access the images stored in ECR. |
| service-outage-monitor-3.global.nats_server | string | `"nats://nats:4222"` | NATS cluster endpoint used by bruin-bridge |
| service-outage-monitor-3.global.papertrail_active | string | `"False"` | Indicates if the logs will be sent to papertrail or not. |
| service-outage-monitor-3.global.papertrail_host | string | `"logs.papertrailapp.com"` | Papertrail host to which the logs will be sent |
| service-outage-monitor-3.global.papertrail_port | string | `"0"` | Papertrail port to which the logs will be sent |
| service-outage-monitor-3.global.redis_hostname | string | `"redis"` | Redis Hostname used to store heavy NATS messages (>1MB) |
| service-outage-monitor-3.image.pullPolicy | string | `"IfNotPresent"` |  |
| service-outage-monitor-3.image.repository | string | `"374050862540.dkr.ecr.us-east-1.amazonaws.com/service-outage-monitor"` |  |
| service-outage-monitor-3.image.tag | string | `""` |  |
| service-outage-monitor-3.replicaCount | int | `1` |  |
| service-outage-monitor-3.resources.limits.cpu | string | `"200m"` |  |
| service-outage-monitor-3.resources.limits.memory | string | `"256Mi"` |  |
| service-outage-monitor-3.resources.requests.cpu | string | `"100m"` |  |
| service-outage-monitor-3.resources.requests.memory | string | `"128Mi"` |  |
| service-outage-monitor-3.service.port | int | `5000` |  |
| service-outage-monitor-3.service.type | string | `"ClusterIP"` |  |
| service-outage-monitor-4.config.capabilities_enabled.bruin_bridge | bool | `true` | Indicate is bruin-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the bruin-bridge service responds correctly to healthcheck calls. |
| service-outage-monitor-4.config.capabilities_enabled.cts_bridge | bool | `true` | Indicate is cts-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the cts-bridge service responds correctly to healthcheck calls. |
| service-outage-monitor-4.config.capabilities_enabled.hawkeye_bridge | bool | `true` | Indicate is hawkeye-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the hawkeye-bridge service responds correctly to healthcheck calls. |
| service-outage-monitor-4.config.capabilities_enabled.lit_bridge | bool | `true` | Indicate is lit-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the lit-bridge service responds correctly to healthcheck calls. |
| service-outage-monitor-4.config.capabilities_enabled.notifier | bool | `true` | Indicate is notifier is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the notifier service responds correctly to healthcheck calls. |
| service-outage-monitor-4.config.capabilities_enabled.t7_bridge | bool | `true` | Indicate is t8-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the t7-bridge service responds correctly to healthcheck calls. |
| service-outage-monitor-4.config.capabilities_enabled.velocloud_bridge | bool | `true` | Indicate is velocloud-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the velocloud-bridge service responds correctly to healthcheck calls. |
| service-outage-monitor-4.config.enable_triage_monitoring | string | `"0"` |  |
| service-outage-monitor-4.config.velocloud_hosts | string | `"host1"` | Velocloud hosts |
| service-outage-monitor-4.config.velocloud_hosts_filter | string | `"host1_filter"` | Filter for Velocloud hosts |
| service-outage-monitor-4.enabled | bool | `true` |  |
| service-outage-monitor-4.global | object | `{"current_environment":"dev","ecr_registry":{"name":"ecr-registry"},"environment":"automation-test","mode":"aws","nats_server":"nats://nats:4222","papertrail_active":"False","papertrail_host":"logs.papertrailapp.com","papertrail_port":"0","redis_hostname":"redis"}` | Global configuration |
| service-outage-monitor-4.global.current_environment | string | `"dev"` | Name of environment for EKS cluster and network resources |
| service-outage-monitor-4.global.ecr_registry.name | string | `"ecr-registry"` | Name of the imagePullSecret created to access the images stored in ECR. |
| service-outage-monitor-4.global.environment | string | `"automation-test"` | Name of environment for helm charts and redis elasticaches used |
| service-outage-monitor-4.global.mode | string | `"aws"` | Indicates if the helm chart will be displayed in an aws or local environment, in case it is local, a specific imagePullSecret will be used to access the images stored in ECR. |
| service-outage-monitor-4.global.nats_server | string | `"nats://nats:4222"` | NATS cluster endpoint used by bruin-bridge |
| service-outage-monitor-4.global.papertrail_active | string | `"False"` | Indicates if the logs will be sent to papertrail or not. |
| service-outage-monitor-4.global.papertrail_host | string | `"logs.papertrailapp.com"` | Papertrail host to which the logs will be sent |
| service-outage-monitor-4.global.papertrail_port | string | `"0"` | Papertrail port to which the logs will be sent |
| service-outage-monitor-4.global.redis_hostname | string | `"redis"` | Redis Hostname used to store heavy NATS messages (>1MB) |
| service-outage-monitor-4.image.pullPolicy | string | `"IfNotPresent"` |  |
| service-outage-monitor-4.image.repository | string | `"374050862540.dkr.ecr.us-east-1.amazonaws.com/service-outage-monitor"` |  |
| service-outage-monitor-4.image.tag | string | `""` |  |
| service-outage-monitor-4.replicaCount | int | `1` |  |
| service-outage-monitor-4.resources.limits.cpu | string | `"200m"` |  |
| service-outage-monitor-4.resources.limits.memory | string | `"256Mi"` |  |
| service-outage-monitor-4.resources.requests.cpu | string | `"100m"` |  |
| service-outage-monitor-4.resources.requests.memory | string | `"128Mi"` |  |
| service-outage-monitor-4.service.port | int | `5000` |  |
| service-outage-monitor-4.service.type | string | `"ClusterIP"` |  |
| service-outage-monitor-triage.config.capabilities_enabled.bruin_bridge | bool | `true` | Indicate is bruin-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the bruin-bridge service responds correctly to healthcheck calls. |
| service-outage-monitor-triage.config.capabilities_enabled.cts_bridge | bool | `true` | Indicate is cts-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the cts-bridge service responds correctly to healthcheck calls. |
| service-outage-monitor-triage.config.capabilities_enabled.hawkeye_bridge | bool | `true` | Indicate is hawkeye-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the hawkeye-bridge service responds correctly to healthcheck calls. |
| service-outage-monitor-triage.config.capabilities_enabled.lit_bridge | bool | `true` | Indicate is lit-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the lit-bridge service responds correctly to healthcheck calls. |
| service-outage-monitor-triage.config.capabilities_enabled.notifier | bool | `true` | Indicate is notifier is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the notifier service responds correctly to healthcheck calls. |
| service-outage-monitor-triage.config.capabilities_enabled.t7_bridge | bool | `true` | Indicate is t8-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the t7-bridge service responds correctly to healthcheck calls. |
| service-outage-monitor-triage.config.capabilities_enabled.velocloud_bridge | bool | `true` | Indicate is velocloud-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the velocloud-bridge service responds correctly to healthcheck calls. |
| service-outage-monitor-triage.config.enable_triage_monitoring | string | `"1"` |  |
| service-outage-monitor-triage.config.velocloud_hosts | string | `""` | Velocloud hosts |
| service-outage-monitor-triage.config.velocloud_hosts_filter | string | `""` | Filter for Velocloud hosts |
| service-outage-monitor-triage.enabled | bool | `true` |  |
| service-outage-monitor-triage.image.pullPolicy | string | `"IfNotPresent"` |  |
| service-outage-monitor-triage.image.repository | string | `"374050862540.dkr.ecr.us-east-1.amazonaws.com/service-outage-monitor"` |  |
| service-outage-monitor-triage.image.tag | string | `""` |  |
| service-outage-monitor-triage.replicaCount | int | `1` |  |
| service-outage-monitor-triage.resources.limits.cpu | string | `"200m"` |  |
| service-outage-monitor-triage.resources.limits.memory | string | `"256Mi"` |  |
| service-outage-monitor-triage.resources.requests.cpu | string | `"100m"` |  |
| service-outage-monitor-triage.resources.requests.memory | string | `"128Mi"` |  |
| service-outage-monitor-triage.service.port | int | `5000` |  |
| service-outage-monitor-triage.service.type | string | `"ClusterIP"` |  |
| t7-bridge | object | `{"config":{"kre_base_url":"","t7_base_url":"","t7_token":""},"fullnameOverride":"","image":{"pullPolicy":"IfNotPresent","repository":"374050862540.dkr.ecr.us-east-1.amazonaws.com/t7-bridge","tag":""},"imagePullSecrets":[],"nameOverride":"","replicaCount":1,"resources":{"limits":{"cpu":"200m","memory":"256Mi"},"requests":{"cpu":"100m","memory":"128Mi"}},"service":{"port":5000,"type":"ClusterIP"}}` | t7-bridge subchart specific configuration |
| t7-bridge.config.kre_base_url | string | `""` | KRE Base URL to make calls for get tickets predictions |
| t7-bridge.config.t7_base_url | string | `""` | Base URL for T7 API |
| tnba-feedback.config.capabilities_enabled.bruin_bridge | bool | `true` | Indicate is bruin-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the bruin-bridge service responds correctly to healthcheck calls. |
| tnba-feedback.config.capabilities_enabled.cts_bridge | bool | `true` | Indicate is cts-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the cts-bridge service responds correctly to healthcheck calls. |
| tnba-feedback.config.capabilities_enabled.hawkeye_bridge | bool | `true` | Indicate is hawkeye-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the hawkeye-bridge service responds correctly to healthcheck calls. |
| tnba-feedback.config.capabilities_enabled.lit_bridge | bool | `true` | Indicate is lit-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the lit-bridge service responds correctly to healthcheck calls. |
| tnba-feedback.config.capabilities_enabled.notifier | bool | `true` | Indicate is notifier is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the notifier service responds correctly to healthcheck calls. |
| tnba-feedback.config.capabilities_enabled.t7_bridge | bool | `true` | Indicate is t8-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the t7-bridge service responds correctly to healthcheck calls. |
| tnba-feedback.config.capabilities_enabled.velocloud_bridge | bool | `true` | Indicate is velocloud-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the velocloud-bridge service responds correctly to healthcheck calls. |
| tnba-feedback.enabled | bool | `true` |  |
| tnba-feedback.image.pullPolicy | string | `"IfNotPresent"` |  |
| tnba-feedback.image.repository | string | `"374050862540.dkr.ecr.us-east-1.amazonaws.com/tnba-feedback"` |  |
| tnba-feedback.image.tag | string | `""` |  |
| tnba-feedback.replicaCount | int | `1` |  |
| tnba-feedback.resources.limits.cpu | string | `"200m"` |  |
| tnba-feedback.resources.limits.memory | string | `"256Mi"` |  |
| tnba-feedback.resources.requests.cpu | string | `"100m"` |  |
| tnba-feedback.resources.requests.memory | string | `"128Mi"` |  |
| tnba-feedback.service.port | int | `5000` |  |
| tnba-feedback.service.type | string | `"ClusterIP"` |  |
| tnba-monitor.config.capabilities_enabled.bruin_bridge | bool | `true` | Indicate is bruin-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the bruin-bridge service responds correctly to healthcheck calls. |
| tnba-monitor.config.capabilities_enabled.cts_bridge | bool | `true` | Indicate is cts-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the cts-bridge service responds correctly to healthcheck calls. |
| tnba-monitor.config.capabilities_enabled.hawkeye_bridge | bool | `true` | Indicate is hawkeye-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the hawkeye-bridge service responds correctly to healthcheck calls. |
| tnba-monitor.config.capabilities_enabled.lit_bridge | bool | `true` | Indicate is lit-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the lit-bridge service responds correctly to healthcheck calls. |
| tnba-monitor.config.capabilities_enabled.notifier | bool | `true` | Indicate is notifier is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the notifier service responds correctly to healthcheck calls. |
| tnba-monitor.config.capabilities_enabled.t7_bridge | bool | `true` | Indicate is t8-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the t7-bridge service responds correctly to healthcheck calls. |
| tnba-monitor.config.capabilities_enabled.velocloud_bridge | bool | `true` | Indicate is velocloud-bridge is going to be activated. If it is true an initContainer will be created in the tnba-monitor deployment that will wait until the velocloud-bridge service responds correctly to healthcheck calls. |
| tnba-monitor.enabled | bool | `true` |  |
| tnba-monitor.image.pullPolicy | string | `"IfNotPresent"` |  |
| tnba-monitor.image.repository | string | `"374050862540.dkr.ecr.us-east-1.amazonaws.com/tnba-monitor"` |  |
| tnba-monitor.image.tag | string | `""` |  |
| tnba-monitor.replicaCount | int | `1` |  |
| tnba-monitor.resources.limits.cpu | string | `"200m"` |  |
| tnba-monitor.resources.limits.memory | string | `"256Mi"` |  |
| tnba-monitor.resources.requests.cpu | string | `"100m"` |  |
| tnba-monitor.resources.requests.memory | string | `"128Mi"` |  |
| tnba-monitor.service.port | int | `5000` |  |
| tnba-monitor.service.type | string | `"ClusterIP"` |  |
| tolerations | list | `[]` |  |
| velocloud-bridge | object | `{"config":{"velocloud_credentials":""},"enabled":true,"image":{"pullPolicy":"IfNotPresent","repository":"374050862540.dkr.ecr.us-east-1.amazonaws.com/velocloud-bridge","tag":""},"replicaCount":1,"resources":{"limits":{"cpu":"200m","memory":"256Mi"},"requests":{"cpu":"100m","memory":"128Mi"}},"service":{"port":5000,"type":"ClusterIP"}}` | velocloud-bridge subchart specific configuration |
| velocloud-bridge.config.velocloud_credentials | string | `""` | Velocloud credentials |


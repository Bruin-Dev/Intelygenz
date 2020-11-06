locals {
  // Project common attributes
  project_name = "mettel-automation"

  // common vars for dev project
  log_prefix = "${var.ENVIRONMENT}-${var.BUILD_NUMBER}"
  nats_server1 = "nats://nats-server-${var.ENVIRONMENT}.${var.ENVIRONMENT}.local:4222"

  // automation-alb local vars
  automation-dev-inbound-security_group-name = "${var.ENVIRONMENT}-inbound"
  automation-dev-inbound-security_group-tag-Name = "${var.ENVIRONMENT}-inbound"
  automation-front_end-lb_target_group-tag-Name = "${var.ENVIRONMENT}-automation-front_end"

  // dns local vars
  automation-route53_record-name = "${var.SUBDOMAIN}.${data.aws_route53_zone.automation.name}"
  automation-zone-service_discovery_private_dns-name = "${var.ENVIRONMENT}.local"

  // automation-redis local vars
  automation-redis-elasticache_cluster-tag-Name = "${var.ENVIRONMENT}-redis"
  automation-redis-security_group-name = "${var.ENVIRONMENT}-redis-sg"
  automation-redis-security_group-tag-Name = "${var.ENVIRONMENT}-redis"
  redis-hostname = aws_elasticache_cluster.automation-redis.cache_nodes[0].address

  // automation-redis-customer-cache local vars
  automation-redis-customer-cache-cluster_id = "${var.ENVIRONMENT}-customer-cache-redis"
  automation-redis-customer-cache-elasticache_cluster-tag-Name = "${var.ENVIRONMENT}-customer-cache-redis"
  automation-redis-customer-cache-subnet_group-name = "${var.ENVIRONMENT}-customer-cache-redis-subnet"
  automation-redis-customer-cache-security_group-name = "${var.ENVIRONMENT}-customer-cache-redis-sg"
  automation-redis-customer-cache-security_group-tag-Name = "${var.ENVIRONMENT}-customer-cache-redis"
  automation-redis-customer-cache-hostname = aws_elasticache_cluster.automation-redis-customer-cache[0].cache_nodes[0].address

  // automation-redis-tnba-feedback-cache local vars
  automation-redis-tnba-feedback-cluster_id = "${var.ENVIRONMENT}-tnba-feedback-cache-redis"
  automation-redis-tnba-feedback-elasticache_cluster-tag-Name = "${var.ENVIRONMENT}-tnba-feedback-redis"
  automation-redis-tnba-feedback-subnet_group-name = "${var.ENVIRONMENT}-tnba-feedback-redis-subnet"
  automation-redis-tnba-feedback-security_group-name = "${var.ENVIRONMENT}-tnba-feedback-redis-sg"
  automation-redis-tnba-feedback-security_group-tag-Name = "${var.ENVIRONMENT}-tnba-feedback-redis"
  automation-redis-tnba-feedback-hostname = aws_elasticache_cluster.automation-redis-tnba-feedback[0].cache_nodes[0].address

  // automation-bruin-brige local vars
  automation-bruin-bridge-image = "${data.aws_ecr_repository.automation-bruin-bridge.repository_url}:${data.external.bruin-bridge-build_number.result["image_tag"]}"
  automation-bruin-bridge-papertrail_prefix = "bruin-bridge-${element(split("-", data.external.bruin-bridge-build_number.result["image_tag"]),2)}"
  automation-bruin-bridge-ecs_task_definition-family = "${var.ENVIRONMENT}-bruin-bridge"
  automation-bruin-bridge_service-security_group-name = "${var.ENVIRONMENT}-bruin-bridge"
  automation-bruin-bridge-resource-name = "${var.ENVIRONMENT}-bruin-bridge"
  automation-bruin-bridge-service-security_group-tag-Name = "${var.ENVIRONMENT}-bruin-bridge"
  automation-bruin-bridge-task_definition = "${aws_ecs_task_definition.automation-bruin-bridge.family}:${aws_ecs_task_definition.automation-bruin-bridge.revision}"
  automation-bruin-bridge-service_discovery_service-name = "bruin-bridge-${var.ENVIRONMENT}"

  // automation-cts-bridge local vars
  automation-cts-bridge-image = "${data.aws_ecr_repository.automation-cts-bridge.repository_url}:${data.external.cts-bridge-build_number.result["image_tag"]}"
  automation-cts-bridge-papertrail_prefix = "cts-bridge-${element(split("-", data.external.cts-bridge-build_number.result["image_tag"]),2)}"
  automation-cts-bridge-ecs_task_definition-family = "${var.ENVIRONMENT}-cts-bridge"
  automation-cts-bridge_service-security_group-name = "${var.ENVIRONMENT}-cts-bridge"
  automation-cts-bridge-resource-name = "${var.ENVIRONMENT}-cts-bridge"
  automation-cts-bridge-service-security_group-tag-Name = "${var.ENVIRONMENT}-cts-bridge"
  automation-cts-bridge-task_definition = "${aws_ecs_task_definition.automation-cts-bridge.family}:${aws_ecs_task_definition.automation-cts-bridge.revision}"
  automation-cts-bridge-service_discovery_service-name = "cts-bridge-${var.ENVIRONMENT}"

  // automation-digi-bridge local vars
  automation-digi-bridge-image = "${data.aws_ecr_repository.automation-digi-bridge.repository_url}:${data.external.digi-bridge-build_number.result["image_tag"]}"
  automation-digi-bridge-papertrail_prefix = "digi-bridge-${element(split("-", data.external.digi-bridge-build_number.result["image_tag"]),2)}"
  automation-digi-bridge-ecs_task_definition-family = "${var.ENVIRONMENT}-digi-bridge"
  automation-digi-bridge_service-security_group-name = "${var.ENVIRONMENT}-digi-bridge"
  automation-digi-bridge-resource-name = "${var.ENVIRONMENT}-digi-bridge"
  automation-digi-bridge-service-security_group-tag-Name = "${var.ENVIRONMENT}-digi-bridge"
  automation-digi-bridge-task_definition = "${aws_ecs_task_definition.automation-digi-bridge.family}:${aws_ecs_task_definition.automation-digi-bridge.revision}"
  automation-digi-bridge-service_discovery_service-name = "digi-bridge-${var.ENVIRONMENT}"

  // customer-cache local vars
  automation-customer-cache-image = "${data.aws_ecr_repository.automation-customer-cache.repository_url}:${data.external.customer-cache-build_number.result["image_tag"]}"
  automation-customer-cache-papertrail_prefix = "customer-cache-${element(split("-", data.external.customer-cache-build_number.result["image_tag"]),2)}"
  automation-customer-cache-ecs_task_definition-family = "${var.ENVIRONMENT}-customer-cache"
  automation-customer-cache_service-security_group-name = "${var.ENVIRONMENT}-customer-cache"
  automation-customer-cache-resource-name = "${var.ENVIRONMENT}-customer-cache"
  automation-customer-cache-service-security_group-tag-Name = "${var.ENVIRONMENT}-customer-cache"
  automation-customer-cache-task_definition = "${aws_ecs_task_definition.automation-customer-cache[0].family}:${aws_ecs_task_definition.automation-customer-cache[0].revision}"
  automation-customer-cache-service_discovery_service-name = "customer-cache-${var.ENVIRONMENT}"

  // automation-dispatch-portal-backend local vars
  automation-dispatch-portal-backend-ecs_task_definition-family = "${var.ENVIRONMENT}-dispatch-portal-backend"
  automation-dispatch-portal-backend-image = "${data.aws_ecr_repository.automation-dispatch-portal-backend.repository_url}:${data.external.dispatch-portal-backend-build_number.result["image_tag"]}"
  automation-dispatch-portal-backend-papertrail_prefix = "dispatch-portal-backend-${element(split("-", data.external.dispatch-portal-backend-build_number.result["image_tag"]),2)}"
  automation-dispatch-portal-backend-service-security_group-name = "${var.ENVIRONMENT}-dispatch-portal-backend"
  automation-dispatch-portal-backend-service-security_group-tag-Name = "${var.ENVIRONMENT}-dispatch-portal-backend"
  automation-dispatch-portal-backend-resource-name = "${var.ENVIRONMENT}-dispatch-portal-backend"
  automation-dispatch-portal-backend-task_definition = "${aws_ecs_task_definition.automation-dispatch-portal-backend.family}:${aws_ecs_task_definition.automation-dispatch-portal-backend.revision}"
  automation-dispatch-portal-backend-service_discovery_service-name = "dispatch-portal-backend-${var.ENVIRONMENT}"

  // automation-dispatch-portal-frontend local vars
  automation-dispatch-portal-frontend-image = "${data.aws_ecr_repository.automation-dispatch-portal-frontend-nextjs.repository_url}:${data.external.dispatch-portal-frontend-nextjs-build_number.result["image_tag"]}"
  automation-dispatch-portal-frontend-nginx-image = "${data.aws_ecr_repository.automation-dispatch-portal-frontend-nginx.repository_url}:${data.external.dispatch-portal-frontend-nginx-build_number.result["image_tag"]}"
  automation-dispatch-portal-service-security_group-name = "${var.ENVIRONMENT}-dispatch-portal-frontend"
  automation-dispatch-portal-frontend-log_prefix = "${var.ENVIRONMENT}-${var.BUILD_NUMBER}"
  automation-dispatch-portal-frontend-ecs_task_definition-family = "${var.ENVIRONMENT}-dispatch-portal-frontend"
  automation-dispatch-portal-frontend-ecs_task_definition = "${var.ENVIRONMENT}-dispatch-portal-frontend"
  automation-dispatch-portal-frontend-service-security_group-name = "${var.ENVIRONMENT}-dispatch-portal-frontend"
  automation-dispatch-portal-frontend-service-security_group-tag-Name = "${var.ENVIRONMENT}-dispatch-portal-frontend"
  automation-dispatch-portal-frontend-ecs_service-name = "${var.ENVIRONMENT}-dispatch-portal-frontend"
  automation-dispatch-portal-frontend-ecs_service-task_definition = "${aws_ecs_task_definition.automation-dispatch-portal-frontend.family}:${aws_ecs_task_definition.automation-dispatch-portal-frontend.revision}"
  automation-dispatch-portal-frontend-service_discovery_service-name = "dispatch-portal-frontend-${var.ENVIRONMENT}"
  automation-dispatch-portal-target_group-name = "${var.ENVIRONMENT}-disp-prtl"
  automation-dispatch-portal-target_group-tag-Name = "${var.ENVIRONMENT}-dispatch-portal"
  automation-dispatch-portal-frontend-nginx-run-mode = "aws"

  // automation-hawkeye-brige local vars
  automation-hawkeye-bridge-image = "${data.aws_ecr_repository.automation-hawkeye-bridge.repository_url}:${data.external.hawkeye-bridge-build_number.result["image_tag"]}"
  automation-hawkeye-bridge-papertrail_prefix = "hawkeye-bridge-${element(split("-", data.external.hawkeye-bridge-build_number.result["image_tag"]),2)}"
  automation-hawkeye-bridge-ecs_task_definition-family = "${var.ENVIRONMENT}-hawkeye-bridge"
  automation-hawkeye-bridge_service-security_group-name = "${var.ENVIRONMENT}-hawkeye-bridge"
  automation-hawkeye-bridge-resource-name = "${var.ENVIRONMENT}-hawkeye-bridge"
  automation-hawkeye-bridge-service-security_group-tag-Name = "${var.ENVIRONMENT}-hawkeye-bridge"
  automation-hawkeye-bridge-task_definition = "${aws_ecs_task_definition.automation-hawkeye-bridge.family}:${aws_ecs_task_definition.automation-hawkeye-bridge.revision}"
  automation-hawkeye-bridge-service_discovery_service-name = "hawkeye-bridge-${var.ENVIRONMENT}"

  // hawkeye-customer-cache local vars
  automation-hawkeye-customer-cache-image = "${data.aws_ecr_repository.automation-hawkeye-customer-cache.repository_url}:${data.external.hawkeye-customer-cache-build_number.result["image_tag"]}"
  automation-hawkeye-customer-cache-papertrail_prefix = "hawkeye-customer-cache-${element(split("-", data.external.hawkeye-customer-cache-build_number.result["image_tag"]),2)}"
  automation-hawkeye-customer-cache-ecs_task_definition-family = "${var.ENVIRONMENT}-hawkeye-customer-cache"
  automation-hawkeye-customer-cache_service-security_group-name = "${var.ENVIRONMENT}-hawkeye-customer-cache"
  automation-hawkeye-customer-cache-resource-name = "${var.ENVIRONMENT}-hawkeye-customer-cache"
  automation-hawkeye-customer-cache-service-security_group-tag-Name = "${var.ENVIRONMENT}-hawkeye-customer-cache"
  automation-hawkeye-customer-cache-task_definition = "${aws_ecs_task_definition.automation-hawkeye-customer-cache[0].family}:${aws_ecs_task_definition.automation-hawkeye-customer-cache[0].revision}"
  automation-hawkeye-customer-cache-service_discovery_service-name = "hawkeye-customer-cache-${var.ENVIRONMENT}"

  // automation-last-contact-report local vars
  automation-last-contact-report-ecs_task_definition-family = "${var.ENVIRONMENT}-last-contact-report"
  automation-last-contact-report-image = "${data.aws_ecr_repository.automation-last-contact-report.repository_url}:${data.external.dispatch-portal-backend-build_number.result["image_tag"]}"
  automation-last-contact-report-papertrail_prefix = "last-contact-report-${element(split("-", data.external.dispatch-portal-backend-build_number.result["image_tag"]),2)}"
  automation-last-contact-report-service-security_group-name = "${var.ENVIRONMENT}-last-contact-report"
  automation-last-contact-report-service-security_group-tag-Name = "${var.ENVIRONMENT}-last-contact-report"
  automation-last-contact-report-resource-name = "${var.ENVIRONMENT}-last-contact-report"
  automation-last-contact-report-task_definition = "${aws_ecs_task_definition.automation-last-contact-report.family}:${aws_ecs_task_definition.automation-last-contact-report.revision}"
  automation-last-contact-service_discovery_service-name = "last-contact-report-${var.ENVIRONMENT}"

  // automation-lit-bridge local vars
  automation-lit-bridge-image = "${data.aws_ecr_repository.automation-lit-bridge.repository_url}:${data.external.lit-bridge-build_number.result["image_tag"]}"
  automation-lit-bridge-papertrail_prefix = "lit-bridge-${element(split("-", data.external.lit-bridge-build_number.result["image_tag"]),2)}"
  automation-lit-bridge-ecs_task_definition-family = "${var.ENVIRONMENT}-lit-bridge"
  automation-lit-bridge_service-security_group-name = "${var.ENVIRONMENT}-lit-bridge"
  automation-lit-bridge-resource-name = "${var.ENVIRONMENT}-lit-bridge"
  automation-lit-bridge-service-security_group-tag-Name = "${var.ENVIRONMENT}-lit-bridge"
  automation-lit-bridge-task_definition = "${aws_ecs_task_definition.automation-lit-bridge.family}:${aws_ecs_task_definition.automation-lit-bridge.revision}"
  automation-lit-bridge-service_discovery_service-name = "lit-bridge-${var.ENVIRONMENT}"

  // automation-lumin-billing-report local vars
  automation-lumin-billing-report-ecs_task_definition-family = "${var.ENVIRONMENT}-lumin-billing-report"
  automation-lumin-billing-report-image = "${data.aws_ecr_repository.automation-lumin-billing-report.repository_url}:${data.external.lumin-billing-report-build_number.result["image_tag"]}"
  automation-lumin-billing-report-service-security_group-name = "${var.ENVIRONMENT}-lumin-billing-report"
  automation-lumin-billing-report-service-security_group-tag-Name = "${var.ENVIRONMENT}-lumin-billing-report"
  automation-lumin-billing-report-resource-name = "${var.ENVIRONMENT}-lumin-billing-report"
  automation-lumin-billing-report-task_definition = "${aws_ecs_task_definition.automation-lumin-billing-report.family}:${aws_ecs_task_definition.automation-lumin-billing-report.revision}"
  automation-lumin-billing-report-service_discovery_service-name = "lumin-billing-report-${var.ENVIRONMENT}"
  automation-lumin-billing-report-papertrail_prefix = "lumin-billing-report-${element(split("-", data.external.lumin-billing-report-build_number.result["image_tag"]),2)}"

  // automation-metrics-grafana local vars
  automation-metrics-grafana-image = "${data.aws_ecr_repository.automation-metrics-grafana.repository_url}:${data.external.grafana-build_number.result["image_tag"]}"
  automation-grafana-papertrail_prefix = "grafana-${element(split("-", data.external.grafana-build_number.result["image_tag"]),2)}"
  automation-metrics-grafana-target_group-name = "${var.ENVIRONMENT}-mts-grafana"
  automation-metrics-grafana-target_group-tag-Name = "${var.ENVIRONMENT}-metrics-grafana"

  // automation-metrics-prometheus local vars
  automation-metrics-prometheus-image = "${data.aws_ecr_repository.automation-metrics-prometheus.repository_url}:${data.external.prometheus-build_number.result["image_tag"]}"
  automation-metrics-prometheus-ecs_task_definition-family = "${var.ENVIRONMENT}-metrics-prometheus"
  automation-metrics-prometheus-service-security_group-name = "${var.ENVIRONMENT}-metrics-prometheus"
  automation-metrics-prometheus-service-security_group-tag-Name = "${var.ENVIRONMENT}-metrics-prometheus"
  automation-metrics-prometheus-ecs_service-name = "${var.ENVIRONMENT}-metrics-prometheus"
  automation-metrics-prometheus-ecs_service-task_definition = "${aws_ecs_task_definition.automation-metrics-prometheus.family}:${aws_ecs_task_definition.automation-metrics-prometheus.revision}"
  automation-metrics-prometheus-service_discovery_service-name = "prometheus-${var.ENVIRONMENT}"
  automation-metrics-prometheus-HTTP_PORT = 9090
  automation-metrics-prometheus-tsdb_path = "/prometheus"
  automation-metrics-prometheus-volume-container_path = "/prometheus"
  automation-metrics-prometheus-tsdb_retention_time = "8h"
  automation-metrics-prometheus-tsdb_block_duration = "1h"
  automation-metrics-prometheus-volume-name = "prometheus_storage-${var.ENVIRONMENT}"
  automation-metrics-prometheus-s3-storage-name = "prometheus-storage-${var.ENVIRONMENT}"
  automation-metrics-prometheus-s3-expiration-days = 14
  automation-metrics-prometheus-s3-storage-tag-Name = "${var.ENVIRONMENT}-metrics-prometheus-storage"

  // automation-metrics-thanos-sidecar local vars
  automation-metrics-thanos-sidecar-image = "${data.aws_ecr_repository.automation-metrics-thanos-sidecar.repository_url}:${data.external.thanos-sidecar-build_number.result["image_tag"]}"
  automation-metrics-thanos-sidecar-GRPC_PORT = 10091
  automation-metrics-thanos-sidecar-HTTP_PORT = 10902
  automation-metrics-thanos-sidecar-objstore-config_file = "/tmp/bucket_config.yaml"

  // automation-metrics-thanos-store-gateway local vars
  automation-metrics-thanos-store-gateway-image = "${data.aws_ecr_repository.automation-metrics-thanos-store-gateway.repository_url}:${data.external.thanos-store-gateway-build_number.result["image_tag"]}"
  automation-metrics-thanos-store-gateway-GRPC_PORT = 10901
  automation-metrics-thanos-store-gateway-HTTP_PORT = 19191
  automation-metrics-thanos-store-gateway-config_file = "/tmp/bucket_config.yaml"

  // automation-metrics-thanos-querier local vars
  automation-metrics-thanos-querier-image = "${data.aws_ecr_repository.automation-metrics-thanos-querier.repository_url}:${data.external.thanos-querier-build_number.result["image_tag"]}"
  automation-metrics-thanos-querier-GRPC_PORT = 10999
  automation-metrics-thanos-querier-HTTP_PORT = 19091

  // automation-nats-server local vars
  automation-nats-server-image = "${data.aws_ecr_repository.automation-nats-server.repository_url}:${data.external.nats-server-build_number.result["image_tag"]}"
  automation-nats-server-ecs_task_definition-family = "${var.ENVIRONMENT}-nats-server"
  automation-nats-server-nats_service-security_group-name = "${var.ENVIRONMENT}-nats-server"
  automation-nats-server-nats_service-security_group-tag-Name = "${var.ENVIRONMENT}-nats-server"
  automation-nats-server-ecs_service-name = "${var.ENVIRONMENT}-nats-server"
  automation-nats-server-ecs_service-task_definition = "${aws_ecs_task_definition.automation-nats-server.family}:${aws_ecs_task_definition.automation-nats-server.revision}"
  automation-nats-server-task_definition_template-container_name = "nats-server"
  automation-nats-server-task_definition_template-natscluster = "nats://0.0.0.0:${var.NATS_SERVER_SEED_CLUSTER_PORT}"

  // automation-nats-server-1 local vars
  automation-nats-server-1-image = "${data.aws_ecr_repository.automation-nats-server.repository_url}:${data.external.nats-server-build_number.result["image_tag"]}"
  automation-nats-server-1-ecs_task_definition-family = "${var.ENVIRONMENT}-nats-server-1"
  automation-nats-server-1-nats_service-security_group-name = "${var.ENVIRONMENT}-nats-server-1"
  automation-nats-server-1-nats_service-security_group-tag-Name = "${var.ENVIRONMENT}-nats-server-1"
  automation-nats-server-1-ecs_service-name = "${var.ENVIRONMENT}-nats-server-1"
  automation-nats-server-1-ecs_service-task_definition = "${aws_ecs_task_definition.automation-nats-server-1.family}:${aws_ecs_task_definition.automation-nats-server-1.revision}"
  automation-nats-server-1-task_definition_template-container_name = "nats-server-1"
  automation-nats-server-1-task_definition_template-natscluster = "nats://localhost:${var.NATS_SERVER_1_CLUSTER_PORT}"
  automation-nats-server-1-task_definition_template-natsroutecluster = "nats://nats-server-${var.ENVIRONMENT}.${var.ENVIRONMENT}.local:${var.NATS_SERVER_SEED_CLUSTER_PORT}"

  // automation-nats-server-2 local vars
  automation-nats-server-2-image = "${data.aws_ecr_repository.automation-nats-server.repository_url}:${data.external.nats-server-build_number.result["image_tag"]}"
  automation-nats-server-2-ecs_task_definition-family = "${var.ENVIRONMENT}-nats-server-2"
  automation-nats-server-2-nats_service-security_group-name = "${var.ENVIRONMENT}-nats-server-2"
  automation-nats-server-2-nats_service-security_group-tag-Name = "${var.ENVIRONMENT}-nats-server-2"
  automation-nats-server-2-ecs_service-name = "${var.ENVIRONMENT}-nats-server-2"
  automation-nats-server-2-ecs_service-task_definition = "${aws_ecs_task_definition.automation-nats-server-2.family}:${aws_ecs_task_definition.automation-nats-server-2.revision}"
  automation-nats-server-2-task_definition_template-container_name = "nats-server-2"
  automation-nats-server-2-task_definition_template-natscluster = "nats://localhost:${var.NATS_SERVER_2_CLUSTER_PORT}"
  automation-nats-server-2-task_definition_template-natsroutecluster = "nats://nats-server-${var.ENVIRONMENT}.${var.ENVIRONMENT}.local:${var.NATS_SERVER_SEED_CLUSTER_PORT}"

  // automation-notifier local vars
  automation-notifier-image = "${data.aws_ecr_repository.automation-notifier.repository_url}:${data.external.notifier-build_number.result["image_tag"]}"
  automation-notifier-papertrail_prefix = "notifier-${element(split("-", data.external.notifier-build_number.result["image_tag"]),2)}"
  automation-notifier-ecs_task_definition-family = "${var.ENVIRONMENT}-notifier"
  automation-notifier-service-security_group-name = "${var.ENVIRONMENT}-notifier"
  automation-notifier-service-security_group-tag-Name = "${var.ENVIRONMENT}-notifier"
  automation-notifier-ecs_service-name = "${var.ENVIRONMENT}-notifier"
  automation-notifier-ecs_service-task_definition = "${aws_ecs_task_definition.automation-notifier.family}:${aws_ecs_task_definition.automation-notifier.revision}"

  // automation-service-affecting-monitor local vars
  automation-service-affecting-monitor-image = "${data.aws_ecr_repository.automation-service-affecting-monitor.repository_url}:${data.external.service-affecting-monitor-build_number.result["image_tag"]}"
  automation-service-affecting-monitor-papertrail_prefix = "service-affecting-monitor-${element(split("-", data.external.service-affecting-monitor-build_number.result["image_tag"]),2)}"
  automation-service-affecting-monitor-ecs_task_definition-family = "${var.ENVIRONMENT}-service-affecting-monitor"
  automation-service-affecting-monitor-service-security_group-name = "${var.ENVIRONMENT}-service-affecting-monitor"
  automation-service-affecting-monitor-service-security_group-tag-Name = "${var.ENVIRONMENT}-service-affecting-monitor"
  automation-service-affecting-monitor-ecs_service-name = "${var.ENVIRONMENT}-service-affecting-monitor"
  automation-service-affecting-monitor-ecs_service-task_definition = "${aws_ecs_task_definition.automation-service-affecting-monitor.family}:${aws_ecs_task_definition.automation-service-affecting-monitor.revision}"
  automation-service-affecting-monitor-service_discovery_service-name = "service-affecting-monitor-${var.ENVIRONMENT}"

  // automation-service-dispatch-monitor local vars
  automation-service-dispatch-monitor-ecs_task_definition-family = "${var.ENVIRONMENT}-service-dispatch-monitor"
  automation-service-dispatch-monitor-image = "${data.aws_ecr_repository.automation-service-dispatch-monitor.repository_url}:${data.external.service-dispatch-monitor-build_number.result["image_tag"]}"
  automation-service-dispatch-monitor-service-security_group-name = "${var.ENVIRONMENT}-service-dispatch-monitor"
  automation-service-dispatch-monitor-service-security_group-tag-Name = "${var.ENVIRONMENT}-service-dispatch-monitor"
  automation-service-dispatch-monitor-resource-name = "${var.ENVIRONMENT}-service-dispatch-monitor"
  automation-service-dispatch-monitor-task_definition = "${aws_ecs_task_definition.automation-service-dispatch-monitor.family}:${aws_ecs_task_definition.automation-service-dispatch-monitor.revision}"
  automation-service-dispatch-monitor-service_discovery_service-name = "service-dispatch-monitor-${var.ENVIRONMENT}"
  automation-service-dispatch-monitor-papertrail_prefix = "service-dispatch-monitor-${element(split("-", data.external.service-dispatch-monitor-build_number.result["image_tag"]),2)}"

  // automation-service-outage-monitor local vars (for all service-outage-monitor services)
  automation-service-outage-monitor-image = "${data.aws_ecr_repository.automation-service-outage-monitor.repository_url}:${data.external.service-outage-monitor-build_number.result["image_tag"]}"
  automation-service-outage-monitor-velocloud_hosts_triage = ""
  automation-service-outage-monitor-velocloud_hosts_filter = "[]"

  // automation-service-outage-monitor-1 local vars
  automation-service-outage-monitor-1-papertrail_prefix = "service-outage-monitor-1-${element(split("-", data.external.service-outage-monitor-build_number.result["image_tag"]),2)}"
  automation-service-outage-monitor-1-container_name = "service-outage-monitor-1"
  automation-service-outage-monitor-1-ecs_task_definition-family = "${var.ENVIRONMENT}-service-outage-monitor-1"
  automation-service-outage-monitor-1-service-security_group-name = "${var.ENVIRONMENT}-service-outage-monitor-1"
  automation-service-outage-monitor-1-service-security_group-tag-Name = "${var.ENVIRONMENT}-service-outage-monitor-1"
  automation-service-outage-monitor-1-ecs_service-name = "${var.ENVIRONMENT}-service-outage-monitor-1"
  automation-service-outage-monitor-1-ecs_service-task_definition = "${aws_ecs_task_definition.automation-service-outage-monitor-1[0].family}:${aws_ecs_task_definition.automation-service-outage-monitor-1[0].revision}"
  automation-service-outage-monitor-1-service_discovery_service-name = "service-outage-monitor-1-${var.ENVIRONMENT}"

  // automation-service-outage-monitor-2 local vars
  automation-service-outage-monitor-2-papertrail_prefix = "service-outage-monitor-2-${element(split("-", data.external.service-outage-monitor-build_number.result["image_tag"]),2)}"
  automation-service-outage-monitor-2-container_name = "service-outage-monitor-2"
  automation-service-outage-monitor-2-ecs_task_definition-family = "${var.ENVIRONMENT}-service-outage-monitor-2"
  automation-service-outage-monitor-2-service-security_group-name = "${var.ENVIRONMENT}-service-outage-monitor-2"
  automation-service-outage-monitor-2-service-security_group-tag-Name = "${var.ENVIRONMENT}-service-outage-monitor-2"
  automation-service-outage-monitor-2-ecs_service-name = "${var.ENVIRONMENT}-service-outage-monitor-2"
  automation-service-outage-monitor-2-ecs_service-task_definition = "${aws_ecs_task_definition.automation-service-outage-monitor-2[0].family}:${aws_ecs_task_definition.automation-service-outage-monitor-2[0].revision}"
  automation-service-outage-monitor-2-service_discovery_service-name = "service-outage-monitor-2-${var.ENVIRONMENT}"

  // automation-service-outage-monitor-3 local vars
  automation-service-outage-monitor-3-papertrail_prefix = "service-outage-monitor-3-${element(split("-", data.external.service-outage-monitor-build_number.result["image_tag"]),2)}"
  automation-service-outage-monitor-3-container_name = "service-outage-monitor-3"
  automation-service-outage-monitor-3-ecs_task_definition-family = "${var.ENVIRONMENT}-service-outage-monitor-3"
  automation-service-outage-monitor-3-service-security_group-name = "${var.ENVIRONMENT}-service-outage-monitor-3"
  automation-service-outage-monitor-3-service-security_group-tag-Name = "${var.ENVIRONMENT}-service-outage-monitor-3"
  automation-service-outage-monitor-3-ecs_service-name = "${var.ENVIRONMENT}-service-outage-monitor-3"
  automation-service-outage-monitor-3-ecs_service-task_definition = "${aws_ecs_task_definition.automation-service-outage-monitor-3[0].family}:${aws_ecs_task_definition.automation-service-outage-monitor-3[0].revision}"
  automation-service-outage-monitor-3-service_discovery_service-name = "service-outage-monitor-3-${var.ENVIRONMENT}"

  // automation-service-outage-monitor-4 local vars
  automation-service-outage-monitor-4-papertrail_prefix = "service-outage-monitor-4-${element(split("-", data.external.service-outage-monitor-build_number.result["image_tag"]),2)}"
  automation-service-outage-monitor-4-container_name = "service-outage-monitor-4"
  automation-service-outage-monitor-4-ecs_task_definition-family = "${var.ENVIRONMENT}-service-outage-monitor-4"
  automation-service-outage-monitor-4-service-security_group-name = "${var.ENVIRONMENT}-service-outage-monitor-4"
  automation-service-outage-monitor-4-service-security_group-tag-Name = "${var.ENVIRONMENT}-service-outage-monitor-4"
  automation-service-outage-monitor-4-ecs_service-name = "${var.ENVIRONMENT}-service-outage-monitor-4"
  automation-service-outage-monitor-4-ecs_service-task_definition = "${aws_ecs_task_definition.automation-service-outage-monitor-4[0].family}:${aws_ecs_task_definition.automation-service-outage-monitor-4[0].revision}"
  automation-service-outage-monitor-4-service_discovery_service-name = "service-outage-monitor-4-${var.ENVIRONMENT}"

  // automation-service-outage-monitor-triage local vars
  automation-service-outage-monitor-triage-papertrail_prefix = "service-outage-monitor-triage-${element(split("-", data.external.service-outage-monitor-build_number.result["image_tag"]),2)}"
  automation-service-outage-monitor-triage-container_name = "service-outage-monitor-triage"
  automation-service-outage-monitor-triage-ecs_task_definition-family = "${var.ENVIRONMENT}-service-outage-monitor-triage"
  automation-service-outage-monitor-triage-service-security_group-name = "${var.ENVIRONMENT}-service-outage-monitor-triage"
  automation-service-outage-monitor-triage-service-security_group-tag-Name = "${var.ENVIRONMENT}-service-outage-monitor-triage"
  automation-service-outage-monitor-triage-ecs_service-name = "${var.ENVIRONMENT}-service-outage-monitor-triage"
  automation-service-outage-monitor-triage-ecs_service-task_definition = "${aws_ecs_task_definition.automation-service-outage-monitor-triage.family}:${aws_ecs_task_definition.automation-service-outage-monitor-triage.revision}"
  automation-service-outage-monitor-triage-service_discovery_service-name = "service-outage-monitor-triage-${var.ENVIRONMENT}"

  // automation-sites-monitor local vars
  automation-sites-monitor-image = "${data.aws_ecr_repository.automation-sites-monitor.repository_url}:${data.external.sites-monitor-build_number.result["image_tag"]}"
  automation-sites-monitor-papertrail_prefix = "sites-monitor-${element(split("-", data.external.sites-monitor-build_number.result["image_tag"]),2)}"
  automation-sites-monitor-log_prefix = "${var.ENVIRONMENT}-${var.BUILD_NUMBER}"
  automation-sites-monitor-ecs_task_definition-family = "${var.ENVIRONMENT}-sites-monitor"
  automation-sites-monitor-service-security_group-name = "${var.ENVIRONMENT}-sites-monitor"
  automation-sites-monitor-service-security_group-tag-Name = "${var.ENVIRONMENT}-sites-monitor"
  automation-sites-monitor-ecs_service-name = "${var.ENVIRONMENT}-sites-monitor"
  automation-sites-monitor-ecs_service-task_definition = "${aws_ecs_task_definition.automation-sites-monitor.family}:${aws_ecs_task_definition.automation-sites-monitor.revision}"
  automation-sites-monitor-service_discovery_service-name = "sites-monitor-${var.ENVIRONMENT}"

  // automation-t7-brige local vars
  automation-t7-bridge-image = "${data.aws_ecr_repository.automation-t7-bridge.repository_url}:${data.external.t7-bridge-build_number.result["image_tag"]}"
  automation-t7-bridge-papertrail_prefix = "t7-bridge-${element(split("-", data.external.t7-bridge-build_number.result["image_tag"]),2)}"
  automation-t7-bridge-ecs_task_definition-family = "${var.ENVIRONMENT}-t7-bridge"
  automation-t7-bridge_service-security_group-name = "${var.ENVIRONMENT}-t7-bridge"
  automation-t7-bridge-resource-name = "${var.ENVIRONMENT}-t7-bridge"
  automation-t7-bridge-service-security_group-tag-Name = "${var.ENVIRONMENT}-t7-bridge"
  automation-t7-bridge-task_definition = "${aws_ecs_task_definition.automation-t7-bridge.family}:${aws_ecs_task_definition.automation-t7-bridge.revision}"
  automation-t7-bridge-service_discovery_service-name = "t7-bridge-${var.ENVIRONMENT}"

  // automation-tnba-monitor local vars
  automation-tnba-monitor-image = "${data.aws_ecr_repository.automation-tnba-monitor.repository_url}:${data.external.tnba-monitor-build_number.result["image_tag"]}"
  automation-tnba-monitor-log_prefix = "${var.ENVIRONMENT}-${var.BUILD_NUMBER}"
  automation-tnba-monitor-ecs_task_definition-family = "${var.ENVIRONMENT}-tnba-monitor"
  automation-tnba-monitor-service-security_group-name = "${var.ENVIRONMENT}-tnba-monitor"
  automation-tnba-monitor-service-security_group-tag-Name = "${var.ENVIRONMENT}-tnba-monitor"
  automation-tnba-monitor-ecs_service-name = "${var.ENVIRONMENT}-tnba-monitor"
  automation-tnba-monitor-ecs_service-task_definition = "${aws_ecs_task_definition.automation-tnba-monitor.family}:${aws_ecs_task_definition.automation-tnba-monitor.revision}"
  automation-tnba-monitor-service_discovery_service-name = "tnba-monitor-${var.ENVIRONMENT}"
  automation-tnba-monitor-papertrail_prefix = "tnba-monitor-${element(split("-", data.external.tnba-monitor-build_number.result["image_tag"]),2)}"

  // automation-tnba-feedback local vars
  automation-tnba-feedback-image = "${data.aws_ecr_repository.automation-tnba-feedback.repository_url}:${data.external.tnba-feedback-build_number.result["image_tag"]}"
  automation-tnba-feedback-log_prefix = "${var.ENVIRONMENT}-${var.BUILD_NUMBER}"
  automation-tnba-feedback-ecs_task_definition-family = "${var.ENVIRONMENT}-tnba-feedback"
  automation-tnba-feedback-service-security_group-name = "${var.ENVIRONMENT}-tnba-feedback"
  automation-tnba-feedback-service-security_group-tag-Name = "${var.ENVIRONMENT}-tnba-feedback"
  automation-tnba-feedback-ecs_service-name = "${var.ENVIRONMENT}-tnba-feedback"
  automation-tnba-feedback-ecs_service-task_definition = "${aws_ecs_task_definition.automation-tnba-feedback[0].family}:${aws_ecs_task_definition.automation-tnba-feedback[0].revision}"
  automation-tnba-feedback-service_discovery_service-name = "tnba-feedback-${var.ENVIRONMENT}"
  automation-tnba-feedback-papertrail_prefix = "tnba-feedback-${element(split("-", data.external.tnba-feedback-build_number.result["image_tag"]),2)}"

  // automation-velocloud-bridge local vars
  automation-velocloud-bridge-image = "${data.aws_ecr_repository.automation-velocloud-bridge.repository_url}:${data.external.velocloud-bridge-build_number.result["image_tag"]}"
  automation-velocloud-bridge-papertrail_prefix = "velocloud-bridge-${element(split("-", data.external.velocloud-bridge-build_number.result["image_tag"]),2)}"
  automation-velocloud-bridge-log_prefix = "${var.ENVIRONMENT}-${var.BUILD_NUMBER}"
  automation-velocloud-bridge-ecs_task_definition-family = "${var.ENVIRONMENT}-velocloud-bridge"
  automation-velocloud-bridge-service-security_group-tag-Name = "${var.ENVIRONMENT}-velocloud-bridge"
  automation-velocloud-bridge-ecs_service-name = "${var.ENVIRONMENT}-velocloud-bridge"
  automation-velocloud-bridge-ecs_service-task_definition = "${aws_ecs_task_definition.automation-velocloud-bridge.family}:${aws_ecs_task_definition.automation-velocloud-bridge.revision}"
  automation-velocloud-bridge-service_discovery_service-name = "velocloud-bridge-${var.ENVIRONMENT}"

  // automation-hawkeye-affecting-monitor local vars
  automation-hawkeye-affecting-monitor-image = "${data.aws_ecr_repository.automation-hawkeye-affecting-monitor.repository_url}:${data.external.hawkeye-affecting-monitor-build_number.result["image_tag"]}"
  automation-hawkeye-affecting-monitor-papertrail_prefix = "hawkeye-affecting-monitor-${element(split("-", data.external.hawkeye-affecting-monitor-build_number.result["image_tag"]),2)}"
  automation-hawkeye-affecting-monitor-ecs_task_definition-family = "${var.ENVIRONMENT}-hawkeye-affecting-monitor"
  automation-hawkeye-affecting-monitor_service-security_group-name = "${var.ENVIRONMENT}-hawkeye-affecting-monitor"
  automation-hawkeye-affecting-monitor-resource-name = "${var.ENVIRONMENT}-hawkeye-affecting-monitor"
  automation-hawkeye-affecting-monitor-service-security_group-tag-Name = "${var.ENVIRONMENT}-hawkeye-affecting-monitor"
  automation-hawkeye-affecting-monitor-task_definition = "${aws_ecs_task_definition.automation-hawkeye-affecting-monitor.family}:${aws_ecs_task_definition.automation-hawkeye-affecting-monitor.revision}"
  automation-hawkeye-affecting-monitor-service_discovery_service-name = "hawkeye-affecting-monitor-${var.ENVIRONMENT}"

  // automation-hawkeye-outage-monitor local vars
  automation-hawkeye-outage-monitor-image = "${data.aws_ecr_repository.automation-hawkeye-outage-monitor.repository_url}:${data.external.hawkeye-outage-monitor-build_number.result["image_tag"]}"
  automation-hawkeye-outage-monitor-papertrail_prefix = "hawkeye-outage-monitor-${element(split("-", data.external.hawkeye-outage-monitor-build_number.result["image_tag"]),2)}"
  automation-hawkeye-outage-monitor-ecs_task_definition-family = "${var.ENVIRONMENT}-hawkeye-outage-monitor"
  automation-hawkeye-outage-monitor_service-security_group-name = "${var.ENVIRONMENT}-hawkeye-outage-monitor"
  automation-hawkeye-outage-monitor-resource-name = "${var.ENVIRONMENT}-hawkeye-outage-monitor"
  automation-hawkeye-outage-monitor-service-security_group-tag-Name = "${var.ENVIRONMENT}-hawkeye-outage-monitor"
  automation-hawkeye-outage-monitor-task_definition = "${aws_ecs_task_definition.automation-hawkeye-outage-monitor.family}:${aws_ecs_task_definition.automation-hawkeye-outage-monitor.revision}"
  automation-hawkeye-outage-monitor-service_discovery_service-name = "hawkeye-outage-monitor-${var.ENVIRONMENT}"

  // metrics local variables
  exceptions_detected_metric-metric_transformation-name = "ExceptionMessagesDetectedInServices-${var.ENVIRONMENT}"
  errors_detected_metric-metric_transformation-name = "ErrorsMessagesDetectedInServices-${var.ENVIRONMENT}"
  running_task_count-metric_transformation-name = "RunningTaskCount"
  exception_detected_metric-metric_transformation-name = "ExceptionMessagesDetectedInServices-${var.ENVIRONMENT}"

  // dashboards local variables
  cluster_dashboard_name = "cluster-${var.ENVIRONMENT}"

  // alarms common local variables
  running_task_count_service-alarm-evaluation_periods = "2"
  running_task_count_service-alarm-period = "300"
  running_task_count_service-alarm-threshold = "3"

  // alarm exception_messages_services local variables
  exception_messages_services_alarm-evaluation_periods = "1"
  exception_messages_services_alarm-period = "180"
  exception_messages_services_alarm-threshold = "5"
  exception_messages_services_alarm-name = "Exception messages detected in services of ECS cluster with name ${var.ENVIRONMENT}"
  exception_messages_services_alarm-tag-Name = "${var.ENVIRONMENT}-exception_messages_detected"

  // alarm error_messages_services local variables
  error_messages_services_alarm-evaluation_periods = "1"
  error_messages_services_alarm-period = "180"
  error_messages_services_alarm-threshold = "5"
  error_messages_services_alarm-name = "Error messages detected in services of ECS cluster with name ${var.ENVIRONMENT}"
  error_messages_services_alarm-tag-Name = "${var.ENVIRONMENT}-error_messages_detected"

  // alarm running_task_count_sites-monitor local variables
  running_task_count_sites-monitor_alarm-name = "Running tasks count of sites-monitor service in ECS cluster with name ${var.ENVIRONMENT}"
  running_task_count_sites-monitor_alarm-tag-Name = "${var.ENVIRONMENT}-running_task_count_sites-monitor"

    // alarm running_task_count_tnba-feedback local variables
  running_task_count_tnba-feedback_alarm-name = "Running tasks count of tnba-feedback service in ECS cluster with name ${var.ENVIRONMENT}"
  running_task_count_tnba-feedback_alarm-tag-Name = "${var.ENVIRONMENT}-running_task_count_tnba-feedback"

  // alarm running_task_count_tnba-monitor local variables
  running_task_count_tnba-monitor_alarm-name = "Running tasks count of tnba-monitor service in ECS cluster with name ${var.ENVIRONMENT}"
  running_task_count_tnba-monitor_alarm-tag-Name = "${var.ENVIRONMENT}-running_task_count_tnba-monitor"

  // alarm running_task_count_bruin-bridge local variables
  running_task_count_bruin-bridge_alarm-name = "Running tasks count of bruin-bridge service in ECS cluster with name ${var.ENVIRONMENT}"
  running_task_count_bruin-bridge_alarm-tag-Name = "${var.ENVIRONMENT}-running_task_count_bruin-bridge"

  // alarm running_task_count_hawkeye-bridge local variables
  running_task_count_hawkeye-bridge_alarm-name = "Running tasks count of hawkeye-bridge service in ECS cluster with name ${var.ENVIRONMENT}"
  running_task_count_hawkeye-bridge_alarm-tag-Name = "${var.ENVIRONMENT}-running_task_count_hawkeye-bridge"

  // alarm running_task_count_service-affecting-monitor local variables
  running_task_count_service-affecting-monitor_alarm-name = "Running tasks count of service-affecting-monitor service in ECS cluster with name ${var.ENVIRONMENT}"
  running_task_count_service-affecting-monitor_alarm-tag-Name = "${var.ENVIRONMENT}-running_task_count_service-affecting-monitor"

  // alarm running_task_count_t7-bridge local variables
  running_task_count_t7-bridge_alarm-name = "Running tasks count of t7-bridge service in ECS cluster with name ${var.ENVIRONMENT}"
  running_task_count_t7-bridge_alarm-tag-Name = "${var.ENVIRONMENT}-running_task_count_t7-bridge"

  // alarm running_task_count_notifier local variables
  running_task_count_notifier_alarm-name = "Running tasks count of notifier service in ECS cluster with name ${var.ENVIRONMENT}"
  running_task_count_notifier_alarm-tag-Name = "${var.ENVIRONMENT}-running_task_count_notifier"

  // alarm running_task_count_metrics-grafana local variables
  running_task_count_metrics-grafana_alarm-name = "Running tasks count of metrics-grafana service in ECS cluster with name ${var.ENVIRONMENT}"
  running_task_count_metrics-grafana_alarm-tag-Name = "${var.ENVIRONMENT}-running_task_count_metrics-grafana"

  // alarm running_task_count_metrics-prometheus local variables
  running_task_count_metrics-prometheus_alarm-name = "Running tasks count of metrics-prometheus service in ECS cluster with name ${var.ENVIRONMENT}"
  running_task_count_metrics-prometheus_alarm-tag-Name = "${var.ENVIRONMENT}-running_task_count_metrics-prometheus"

  // alarm running_task_count_nats-server local variables
  running_task_count_nats-server_alarm-name = "Running tasks count of nats-server service in ECS cluster with name ${var.ENVIRONMENT}"
  running_task_count_nats-server_alarm-tag-Name = "${var.ENVIRONMENT}-running_task_count_nats-server"

  // alarm running_task_count_nats-server-1 local variables
  running_task_count_nats-server-1_alarm-name = "Running tasks count of nats-server-1 service in ECS cluster with name ${var.ENVIRONMENT}"
  running_task_count_nats-server-1_alarm-tag-Name = "${var.ENVIRONMENT}-running_task_count_nats-server-1"

  // alarm running_task_count_nats-server-2 local variables
  running_task_count_nats-server-2_alarm-name = "Running tasks count of nats-server-2 service in ECS cluster with name ${var.ENVIRONMENT}"
  running_task_count_nats-server-2_alarm-tag-Name = "${var.ENVIRONMENT}-running_task_count_nats-server-2"

  // alarm running_task_count_service-dispatch-monitor local variables
  running_task_count_service-dispatch-monitor_alarm-name = "Running tasks count of service-dispatch-monitor service in ECS cluster with name ${var.ENVIRONMENT}"
  running_task_count_service-dispatch-monitor_alarm-tag-Name = "${var.ENVIRONMENT}-running_task_count_service-dispatch-monitor"

  // alarm running_task_count_service-outage-monitor (Velocloud host# 1) local variables
  running_task_count_service-outage-monitor-1_alarm-name = "Running tasks count of service-outage-monitor service # 1 in ECS cluster with name ${var.ENVIRONMENT}"
  running_task_count_service-outage-monitor-1_alarm-tag-Name = "${var.ENVIRONMENT}-running_task_count_service-outage-monitor-1"

  // alarm running_task_count_service-outage-monitor (Velocloud host# 2) local variables
  running_task_count_service-outage-monitor-2_alarm-name = "Running tasks count of service-outage-monitor service # 2 in ECS cluster with name ${var.ENVIRONMENT}"
  running_task_count_service-outage-monitor-2_alarm-tag-Name = "${var.ENVIRONMENT}-running_task_count_service-outage-monitor-2"

  // alarm running_task_count_service-outage-monitor (Velocloud host# 3) local variables
  running_task_count_service-outage-monitor-3_alarm-name = "Running tasks count of service-outage-monitor service # 3 in ECS cluster with name ${var.ENVIRONMENT}"
  running_task_count_service-outage-monitor-3_alarm-tag-Name = "${var.ENVIRONMENT}-running_task_count_service-outage-monitor-3"

  // alarm running_task_count_service-outage-monitor (Velocloud host# 4) local variables
  running_task_count_service-outage-monitor-4_alarm-name = "Running tasks count of service-outage-monitor service # 4 in ECS cluster with name ${var.ENVIRONMENT}"
  running_task_count_service-outage-monitor-4_alarm-tag-Name = "${var.ENVIRONMENT}-running_task_count_service-outage-monitor-4"

  // alarm running_task_count_service-outage-monitor (triage monitoring) local variables
  running_task_count_service-outage-monitor-triage_alarm-name = "Running tasks count of service-outage-monitor service for triage in ECS cluster with name ${var.ENVIRONMENT}"
  running_task_count_service-outage-monitor-triage_alarm-tag-Name = "${var.ENVIRONMENT}-running_task_count_service-outage-monitor-triage"

  // alarm running_task_count_lumin-billing-report local variables
  running_task_count_lumin-billing-report_alarm-name = "Running tasks count of lumin-billing-report service in ECS cluster with name ${var.ENVIRONMENT}"
  running_task_count_lumin-billing-report_alarm-tag-Name = "${var.ENVIRONMENT}-running_task_count_lumin-billing-report"

  // alarm running_task_count_last-contact-report local variables
  running_task_count_last-contact-report_alarm-name = "Running tasks count of last-contact-report service in ECS cluster with name ${var.ENVIRONMENT}"
  running_task_count_last-contact-report_alarm-tag-Name = "${var.ENVIRONMENT}-running_task_count_last-contact-report"

  // alarm running_task_count_velocloud-bridge local variables
  running_task_count_velocloud-bridge_alarm-name = "Running tasks count of velocloud-bridge service in ECS cluster with name ${var.ENVIRONMENT}"
  running_task_count_velocloud-bridge_alarm-tag-Name = "${var.ENVIRONMENT}-running_task_count_velocloud-bridge"

  // alarm running_task_count_dispatch-portal-frontend local variables
  running_task_count_dispatch-portal-frontend_alarm-name = "Running tasks count of dispatch-portal-frontend service in ECS cluster with name ${var.ENVIRONMENT}"
  running_task_count_dispatch-portal-frontend_alarm-tag-Name = "${var.ENVIRONMENT}-running_task_count_dispatch-portal-frontend"

  // alarm running_task_count_dispatch-portal-backend local variables
  running_task_count_dispatch-portal-backend_alarm-name = "Running tasks count of dispatch-portal-backend service in ECS cluster with name ${var.ENVIRONMENT}"
  running_task_count_dispatch-portal-backend_alarm-tag-Name = "${var.ENVIRONMENT}-running_task_count_dispatch-portal-backend"

  // alarm running_task_count_cts-bridge local variables
  running_task_count_cts-bridge_alarm-name = "Running tasks count of cts-bridge service in ECS cluster with name ${var.ENVIRONMENT}"
  running_task_count_cts-bridge_alarm-tag-Name = "${var.ENVIRONMENT}-running_task_count_cts-bridge"

  // alarm running_task_count_customer-cache local variables
  running_task_count_customer-cache_alarm-name = "Running tasks count of customer-cache service in ECS cluster with name ${var.ENVIRONMENT}"
  running_task_count_customer-cache_alarm-tag-Name = "${var.ENVIRONMENT}-running_task_count_customer-cache"

  // alarm running_task_count_hawkeye-affecting-monitor local variables
  running_task_count_hawkeye-affecting-monitor_alarm-name = "Running tasks count of hawkeye-affecting-monitor service in ECS cluster with name ${var.ENVIRONMENT}"
  running_task_count_hawkeye-affecting-monitor_alarm-tag-Name = "${var.ENVIRONMENT}-running_task_count_hawkeye-affecting-monitor"

  // alarm running_task_count_hawkeye_customer-cache local variables
  running_task_count_hawkeye-customer-cache_alarm-name = "Running tasks count of hawkeye-customer-cache service in ECS cluster with name ${var.ENVIRONMENT}"
  running_task_count_hawkeye-customer-cache_alarm-tag-Name = "${var.ENVIRONMENT}-running_task_count_hawkeye-customer-cache"

  // alarm running_task_count_hawkeye-outage-monitor local variables
  running_task_count_hawkeye-outage-monitor_alarm-name = "Running tasks count of hawkeye-outage-monitor service in ECS cluster with name ${var.ENVIRONMENT}"
  running_task_count_hawkeye-outage-monitor_alarm-tag-Name = "${var.ENVIRONMENT}-running_task_count_hawkeye-outage-monitor"

  // alarm running_task_count_digi-bridge local variables
  running_task_count_digi-bridge_alarm-name = "Running tasks count of digi-bridge service in ECS cluster with name ${var.ENVIRONMENT}"
  running_task_count_digi-bridge_alarm-tag-Name = "${var.ENVIRONMENT}-running_task_count_digi-bridge"

  // cloudformation local variables
  stack_alarms-errors_exceptions_messages_in_services-name = "SnsTopicMetTelAutomationAlarms-${var.ENVIRONMENT}"
  cloudformation_sns_stack_alarms_errors_exceptions_messages-description-stack="MetTel Notificacion Topic for Alarms in ECS cluster with name ${var.ENVIRONMENT}"
  cloudformation_sns_stack_alarms_errors_exceptions_messages-description-operator_email="Email address to notify if there are any active alarms in MetTel automation infrastructure"

}

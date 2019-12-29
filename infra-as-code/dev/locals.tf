locals {
  // common vars for dev project
  log_prefix = "${var.ENVIRONMENT}-${var.BUILD_NUMBER}"
  nats_server1 = "nats://nats-server-${var.ENVIRONMENT}.${var.ENVIRONMENT}.local:4222"
  slack_url = "https://hooks.slack.com/services/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"

  // automation-alb local vars
  automation-dev-inbound-security_group-name = "${var.ENVIRONMENT}-inbound"
  automation-dev-inbound-security_group-tag-Name = "${var.ENVIRONMENT}-inbound"
  automation-front_end-lb_target_group-tag-Name = "${var.ENVIRONMENT}-automation-front_end"

  // dns local vars
  automation-route53_record-name = "${var.SUBDOMAIN}.${data.aws_route53_zone.automation.name}"
  automation-zone-service_discovery_private_dns-name = "${var.ENVIRONMENT}.local"

  // automation-nats-server local vars
  automation-nats-server-image = "${data.aws_ecr_repository.automation-nats-server.repository_url}:${var.NATS_MODULE_VERSION}"
  automation-nats-server-ecs_task_definition-family = "${var.ENVIRONMENT}-nats-server"
  automation-nats-server-nats_service-security_group-name = "${var.ENVIRONMENT}-nats-server"
  automation-nats-server-nats_service-security_group-tag-Name = "${var.ENVIRONMENT}-nats-server"
  automation-nats-server-ecs_service-name = "${var.ENVIRONMENT}-nats-server"
  automation-nats-server-ecs_service-task_definition = "${aws_ecs_task_definition.automation-nats-server.family}:${aws_ecs_task_definition.automation-nats-server.revision}"
  automation-nats-server-task_definition_template-container_name = "nats-server"
  automation-nats-server-task_definition_template-natscluster = "nats://0.0.0.0:${var.NATS_SERVER_SEED_CLUSTER_PORT}"

  // automation-redis local vars
  automation-redis-elasticache_cluster-tag-Name = "${var.ENVIRONMENT}-redis"
  automation-redis-security_group-name = "${var.ENVIRONMENT}-redis-sg"
  automation-redis-security_group-tag-Name = "${var.ENVIRONMENT}-redis"

  // automation-nats-server-2 local vars
  automation-nats-server-2-image = "${data.aws_ecr_repository.automation-nats-server.repository_url}:${var.NATS_MODULE_VERSION}"
  automation-nats-server-2-ecs_task_definition-family = "${var.ENVIRONMENT}-nats-server-2"
  automation-nats-server-2-nats_service-security_group-name = "${var.ENVIRONMENT}-nats-server-2"
  automation-nats-server-2-nats_service-security_group-tag-Name = "${var.ENVIRONMENT}-nats-server-2"
  automation-nats-server-2-ecs_service-name = "${var.ENVIRONMENT}-nats-server-2"
  automation-nats-server-2-ecs_service-task_definition = "${aws_ecs_task_definition.automation-nats-server-2.family}:${aws_ecs_task_definition.automation-nats-server-2.revision}"
  automation-nats-server-2-task_definition_template-container_name = "nats-server-2"
  automation-nats-server-2-task_definition_template-natscluster = "nats://localhost:${var.NATS_SERVER_2_CLUSTER_PORT}"
  automation-nats-server-2-task_definition_template-natsroutecluster = "nats://nats-server-${var.ENVIRONMENT}.${var.ENVIRONMENT}.local:${var.NATS_SERVER_SEED_CLUSTER_PORT}"

  // bruin-brige local vars
  automation-bruin-bridge-image = "${data.aws_ecr_repository.automation-bruin-bridge.repository_url}:${var.BUILD_NUMBER}"
  automation-bruin-bridge-ecs_task_definition-family = "${var.ENVIRONMENT}-bruin-bridge"
  automation-bruin-bridge_service-security_group-name = "${var.ENVIRONMENT}-bruin-bridge"
  automation-bruin-bridge-resource-name = "${var.ENVIRONMENT}-bruin-bridge"
  automation-bruin-bridge-service-security_group-tag-Name = "${var.ENVIRONMENT}-bruin-bridge"
  automation-bruin-bridge-task_definition = "${aws_ecs_task_definition.automation-bruin-bridge.family}:${aws_ecs_task_definition.automation-bruin-bridge.revision}"
  automation-bruin-bridge-service_discovery_service-name = "bruin-bridge-${var.ENVIRONMENT}"

  // t7-brige local vars
  automation-t7-bridge-image = "${data.aws_ecr_repository.automation-t7-bridge.repository_url}:${var.BUILD_NUMBER}"
  automation-t7-bridge-ecs_task_definition-family = "${var.ENVIRONMENT}-t7-bridge"
  automation-t7-bridge_service-security_group-name = "${var.ENVIRONMENT}-t7-bridge"
  automation-t7-bridge-resource-name = "${var.ENVIRONMENT}-t7-bridge"
  automation-t7-bridge-service-security_group-tag-Name = "${var.ENVIRONMENT}-t7-bridge"
  automation-t7-bridge-task_definition = "${aws_ecs_task_definition.automation-t7-bridge.family}:${aws_ecs_task_definition.automation-t7-bridge.revision}"
  automation-t7-bridge-service_discovery_service-name = "t7-bridge-${var.ENVIRONMENT}"

  // automation-last-contact-report local vars
  automation-last-contact-report-ecs_task_definition-family = "${var.ENVIRONMENT}-last-contact-report"
  automation-last-contact-report-image = "${data.aws_ecr_repository.automation-last-contact-report.repository_url}:${var.BUILD_NUMBER}"
  automation-last-contact-report-service-security_group-name = "${var.ENVIRONMENT}-last-contact-report"
  automation-last-contact-report-service-security_group-tag-Name = "${var.ENVIRONMENT}-last-contact-report"
  automation-last-contact-report-resource-name = "${var.ENVIRONMENT}-last-contact-report"
  automation-last-contact-report-task_definition = "${aws_ecs_task_definition.automation-last-contact-report.family}:${aws_ecs_task_definition.automation-last-contact-report.revision}"
  automation-last-contact-service_discovery_service-name = "last-contact-report-${var.ENVIRONMENT}"

  // automation-metrics-grafana local vars
  automation-metrics-grafana-image = "${data.aws_ecr_repository.automation-metrics-grafana.repository_url}:${var.BUILD_NUMBER}"
  automation-metrics-grafana-ecs_task_definition-family = "${var.ENVIRONMENT}-metrics-grafana"
  automation-metrics-grafana-service-security_group-name = "${var.ENVIRONMENT}-metrics-grafana"
  automation-metrics-grafana-service-security_group-tag-Name = "${var.ENVIRONMENT}-metrics-grafana"
  automation-metrics-grafana-ecs_service-name = "${var.ENVIRONMENT}-metrics-grafana"
  automation-metrics-grafana-target_group-name = "${var.ENVIRONMENT}-mts-grafana"
  automation-metrics-grafana-target_group-tag-Name = "${var.ENVIRONMENT}-metrics-grafana"

  // automation-metrics-prometheus local vars
  automation-metrics-prometheus-image = "${data.aws_ecr_repository.automation-metrics-prometheus.repository_url}:${var.BUILD_NUMBER}"
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
  automation-metrics-prometheus-s3-storage-tag-Name = "${var.ENVIRONMENT}-metrics-prometheus-storage"

  // automation-metrics-thanos-sidecar local vars
  automation-metrics-thanos-sidecar-image = "${data.aws_ecr_repository.automation-metrics-thanos-sidecar.repository_url}:${var.BUILD_NUMBER}"
  automation-metrics-thanos-sidecar-GRPC_PORT = 10091
  automation-metrics-thanos-sidecar-HTTP_PORT = 10902
  automation-metrics-thanos-sidecar-objstore-config_file = "/tmp/bucket_config.yaml"

  // automation-metrics-thanos-store-gateway local vars
  automation-metrics-thanos-store-gateway-image = "${data.aws_ecr_repository.automation-metrics-thanos-store-gateway.repository_url}:${var.BUILD_NUMBER}"
  automation-metrics-thanos-store-gateway-GRPC_PORT = 10901
  automation-metrics-thanos-store-gateway-HTTP_PORT = 19191
  automation-metrics-thanos-store-gateway-config_file = "/tmp/bucket_config.yaml"

  // automation-metrics-thanos-querier local vars
  automation-metrics-thanos-querier-image = "${data.aws_ecr_repository.automation-metrics-thanos-querier.repository_url}:${var.BUILD_NUMBER}"
  automation-metrics-thanos-querier-GRPC_PORT = 10999
  automation-metrics-thanos-querier-HTTP_PORT = 19091

  // automation-notifier local vars
  automation-notifier-image = "${data.aws_ecr_repository.automation-notifier.repository_url}:${var.BUILD_NUMBER}"
  automation-notifier-ecs_task_definition-family = "${var.ENVIRONMENT}-notifier"
  automation-notifier-service-security_group-name = "${var.ENVIRONMENT}-notifier"
  automation-notifier-service-security_group-tag-Name = "${var.ENVIRONMENT}-notifier"
  automation-notifier-ecs_service-name = "${var.ENVIRONMENT}-notifier"
  automation-notifier-ecs_service-task_definition = "${aws_ecs_task_definition.automation-notifier.family}:${aws_ecs_task_definition.automation-notifier.revision}"

  // automation-service-affecting-monitor local vars
  automation-service-affecting-monitor-image = "${data.aws_ecr_repository.automation-service-affecting-monitor.repository_url}:${var.BUILD_NUMBER}"
  automation-service-affecting-monitor-ecs_task_definition-family = "${var.ENVIRONMENT}-service-affecting-monitor"
  automation-service-affecting-monitor-service-security_group-name = "${var.ENVIRONMENT}-service-affecting-monitor"
  automation-service-affecting-monitor-service-security_group-tag-Name = "${var.ENVIRONMENT}-service-affecting-monitor"
  automation-service-affecting-monitor-ecs_service-name = "${var.ENVIRONMENT}-service-affecting-monitor"
  automation-service-affecting-monitor-ecs_service-task_definition = "${aws_ecs_task_definition.automation-service-affecting-monitor.family}:${aws_ecs_task_definition.automation-service-affecting-monitor.revision}"
  automation-service-affecting-monitor-service_discovery_service-name = "service-affecting-monitor-${var.ENVIRONMENT}"

  // automation-service-outage-monitor local vars
  automation-service-outage-monitor-image = "${data.aws_ecr_repository.automation-service-outage-monitor.repository_url}:${var.BUILD_NUMBER}"
  automation-service-outage-monitor-ecs_task_definition-family = "${var.ENVIRONMENT}-service-outage-monitor"
  automation-service-outage-monitor-service-security_group-name = "${var.ENVIRONMENT}-service-outage-monitor"
  automation-service-outage-monitor-service-security_group-tag-Name = "${var.ENVIRONMENT}-service-outage-monitor"
  automation-service-outage-monitor-ecs_service-name = "${var.ENVIRONMENT}-service-outage-monitor"
  automation-service-outage-monitor-ecs_service-task_definition = "${aws_ecs_task_definition.automation-service-outage-monitor.family}:${aws_ecs_task_definition.automation-service-outage-monitor.revision}"
  automation-service-outage-monitor-service_discovery_service-name = "service-outage-monitor-${var.ENVIRONMENT}"

  // automation-service-outage-triage local vars
  automation-service-outage-triage-image = "${data.aws_ecr_repository.automation-service-outage-triage.repository_url}:${var.BUILD_NUMBER}"
  automation-service-outage-triage-log_prefix = "${var.ENVIRONMENT}-${var.BUILD_NUMBER}"
  automation-service-outage-triage-ecs_task_definition-family = "${var.ENVIRONMENT}-service-outage-triage"
  automation-service-outage-triage-service-security_group-name = "${var.ENVIRONMENT}-service-outage-triage"
  automation-service-outage-triage-service-security_group-tag-Name = "${var.ENVIRONMENT}-service-outage-triage"
  automation-service-outage-triage-ecs_service-name = "${var.ENVIRONMENT}-service-outage-triage"
  automation-service-outage-triage-ecs_service-task_definition = "${aws_ecs_task_definition.automation-service-outage-triage.family}:${aws_ecs_task_definition.automation-service-outage-triage.revision}"
  automation-service-outage-triage-service_discovery_service-name = "service-outage-triage-${var.ENVIRONMENT}"

  // automation-velocloud-bridge local vars
  automation-velocloud-bridge-image = "${data.aws_ecr_repository.automation-velocloud-bridge.repository_url}:${var.BUILD_NUMBER}"
  automation-velocloud-bridge-log_prefix = "${var.ENVIRONMENT}-${var.BUILD_NUMBER}"
  automation-velocloud-bridge-ecs_task_definition-family = "${var.ENVIRONMENT}-velocloud-bridge"
  automation-velocloud-bridge-service-security_group-tag-Name = "${var.ENVIRONMENT}-velocloud-bridge"
  automation-velocloud-bridge-ecs_service-name = "${var.ENVIRONMENT}-velocloud-bridge"
  automation-velocloud-bridge-ecs_service-task_definition = "${aws_ecs_task_definition.automation-velocloud-bridge.family}:${aws_ecs_task_definition.automation-velocloud-bridge.revision}"
  automation-velocloud-bridge-service_discovery_service-name = "velocloud-bridge-${var.ENVIRONMENT}"

  // automation-sites-monitor local vars
  automation-sites-monitor-image = "${data.aws_ecr_repository.automation-sites-monitor.repository_url}:${var.BUILD_NUMBER}"
  automation-sites-monitor-log_prefix = "${var.ENVIRONMENT}-${var.BUILD_NUMBER}"
  automation-sites-monitor-ecs_task_definition-family = "${var.ENVIRONMENT}-sites-monitor"
  automation-sites-monitor-service-security_group-name = "${var.ENVIRONMENT}-sites-monitor"
  automation-sites-monitor-service-security_group-tag-Name = "${var.ENVIRONMENT}-sites-monitor"
  automation-sites-monitor-ecs_service-name = "${var.ENVIRONMENT}-sites-monitor"
  automation-sites-monitor-ecs_service-task_definition = "${aws_ecs_task_definition.automation-sites-monitor.family}:${aws_ecs_task_definition.automation-sites-monitor.revision}"
  automation-sites-monitor-service_discovery_service-name = "sites-monitor-${var.ENVIRONMENT}"

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

  // alarm running_task_count_bruin-bridge local variables
  running_task_count_bruin-bridge_alarm-name = "Running tasks count of bruin-bridge service in ECS cluster with name ${var.ENVIRONMENT}"
  running_task_count_bruin-bridge_alarm-tag-Name = "${var.ENVIRONMENT}-running_task_count_bruin-bridge"

  // alarm running_task_count_service-outage-triage local variables
  running_task_count_service-outage-triage_alarm-name = "Running tasks count of service-outage-triage service in ECS cluster with name ${var.ENVIRONMENT}"
  running_task_count_service-outage-triage_alarm-tag-Name = "${var.ENVIRONMENT}-running_task_count_service-outage-triage"

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

  // alarm running_task_count_service-outage-monitor local variables
  running_task_count_service-outage-monitor_alarm-name = "Running tasks count of service-outage-monitor service in ECS cluster with name ${var.ENVIRONMENT}"
  running_task_count_service-outage-monitor_alarm-tag-Name = "${var.ENVIRONMENT}-running_task_count_service-outage-monitor"

  // alarm running_task_count_last-contact-report local variables
  running_task_count_last-contact-report_alarm-name = "Running tasks count of last-contact-report service in ECS cluster with name ${var.ENVIRONMENT}"
  running_task_count_last-contact-report_alarm-tag-Name = "${var.ENVIRONMENT}-running_task_count_last-contact-report"

  // alarm running_task_count_velocloud-bridge_
  running_task_count_velocloud-bridge_alarm-name = "Running tasks count of velocloud-bridge service in ECS cluster with name ${var.ENVIRONMENT}"
  running_task_count_velocloud-bridge_alarm-tag-Name = "${var.ENVIRONMENT}-running_task_count_velocloud-bridge"

  // cloudformation local variables
  stack_alarms-errors_exceptions_messages_in_services-name = "SnsTopicMetTelAutomationAlarms-${var.ENVIRONMENT}"
  cloudformation_sns_stack_alarms_errors_exceptions_messages-description-stack="MetTel Notificacion Topic for Alarms in ECS cluster with name ${var.ENVIRONMENT}"
  cloudformation_sns_stack_alarms_errors_exceptions_messages-description-operator_email="Email address to notify if there are any active alarms in MetTel automation infrastructure"

  // automation-nats-server-1 local vars
  automation-nats-server-1-image = "${data.aws_ecr_repository.automation-nats-server.repository_url}:${var.NATS_MODULE_VERSION}"
  automation-nats-server-1-ecs_task_definition-family = "${var.ENVIRONMENT}-nats-server-1"
  automation-nats-server-1-nats_service-security_group-name = "${var.ENVIRONMENT}-nats-server-1"
  automation-nats-server-1-nats_service-security_group-tag-Name = "${var.ENVIRONMENT}-nats-server-1"
  automation-nats-server-1-ecs_service-name = "${var.ENVIRONMENT}-nats-server-1"
  automation-nats-server-1-ecs_service-task_definition = "${aws_ecs_task_definition.automation-nats-server-1.family}:${aws_ecs_task_definition.automation-nats-server-1.revision}"
  automation-nats-server-1-task_definition_template-container_name = "nats-server-1"
  automation-nats-server-1-task_definition_template-natscluster = "nats://localhost:${var.NATS_SERVER_1_CLUSTER_PORT}"
  automation-nats-server-1-task_definition_template-natsroutecluster = "nats://nats-server-${var.ENVIRONMENT}.${var.ENVIRONMENT}.local:${var.NATS_SERVER_SEED_CLUSTER_PORT}"

}

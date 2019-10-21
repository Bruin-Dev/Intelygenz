locals {
  // common vars for ecs-services project
  nats_server1 = "nats://nats-server-${var.ENVIRONMENT}.${var.ENVIRONMENT}.local:4222"
  log_prefix = "${var.ENVIRONMENT}-${var.BUILD_NUMBER}"
  slack_url = "https://hooks.slack.com/services/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"

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
  automation-metrics-grafana-ecs_task_definition = "${aws_ecs_task_definition.automation-metrics-grafana.family}:${aws_ecs_task_definition.automation-metrics-grafana.revision}"
  automation-metrics-grafana-target_group-name = "${var.ENVIRONMENT}-mts-grafana"

  // automation-metrics-prometheus local vars
  automation-metrics-prometheus-image = "${data.aws_ecr_repository.automation-metrics-prometheus.repository_url}:${var.BUILD_NUMBER}"
  automation-metrics-prometheus-ecs_task_definition-family = "${var.ENVIRONMENT}-metrics-prometheus"
  automation-metrics-prometheus-service-security_group-name = "${var.ENVIRONMENT}-metrics-prometheus"
  automation-metrics-prometheus-service-security_group-tag-Name = "${var.ENVIRONMENT}-metrics-prometheus"
  automation-metrics-prometheus-ecs_service-name = "${var.ENVIRONMENT}-metrics-prometheus"
  automation-metrics-prometheus-ecs_service-task_definition = "${aws_ecs_task_definition.automation-metrics-prometheus.family}:${aws_ecs_task_definition.automation-metrics-prometheus.revision}"
  automation-metrics-prometheus-service_discovery_service-name = "prometheus-${var.ENVIRONMENT}"

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

  // automation-velocloud-orchestrator local vars
  automation-velocloud-orchestrator-image = "${data.aws_ecr_repository.automation-velocloud-orchestrator.repository_url}:${var.BUILD_NUMBER}"
  automation-velocloud-orchestrator-log_prefix = "${var.ENVIRONMENT}-${var.BUILD_NUMBER}"
  automation-velocloud-orchestrator-ecs_task_definition-family = "${var.ENVIRONMENT}-velocloud-orchestrator"
  automation-velocloud-orchestrator-service-security_group-name = "${var.ENVIRONMENT}-velocloud-orchestrator"
  automation-velocloud-orchestrator-service-security_group-tag-Name = "${var.ENVIRONMENT}-velocloud-orchestrator"
  automation-velocloud-orchestrator-ecs_service-name = "${var.ENVIRONMENT}-velocloud-orchestrator"
  automation-velocloud-orchestrator-ecs_service-task_definition = "${aws_ecs_task_definition.automation-velocloud-orchestrator.family}:${aws_ecs_task_definition.automation-velocloud-orchestrator.revision}"
  automation-velocloud-orchestrator-service_discovery_service-name = "velocloud-orchestrator-${var.ENVIRONMENT}"

  // metrics local variables
  exception_detected_metric-metric_transformation-name = "ExceptionMessagesDetectedInServices"

  // dashboards local variables
  cluster_dashboard_name = "cluster-${var.ENVIRONMENT}"

  // alarms local variables
  cluster_task_running-alarm_name = "tasks_running-${var.ENVIRONMENT}"

  // cloudfourmation local variables
  stack_alarms-errors_exceptions_messages_in_services-name = "SnsTopicAlarmErrorMessagesInServicesStack"
}

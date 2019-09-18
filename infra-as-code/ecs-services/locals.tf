locals {
  // common vars for ecs-services project
  nats_server1 = "nats://nats-server.${var.ENVIRONMENT}.local:4222"
  log_prefix = "${var.ENVIRONMENT}-${var.BUILD_NUMBER}"
  slack_url = "https://hooks.slack.com/services/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"

  // bruin-brige local vars
  automation-bruin-bridge-image = "${data.aws_ecr_repository.automation-bruin-bridge.repository_url}:${var.BUILD_NUMBER}"
  automation-bruin-bridge-ecs_task_definition-family = "${var.ENVIRONMENT}-bruin-bridge"
  automation-bruin-bridge_service-security_group-name = "${var.ENVIRONMENT}-bruin-bridge"
  automation-bruin-bridge-resource-name = "${var.ENVIRONMENT}-bruin-bridge"
  automation-bruin-bridge-service-security_group-tag-Name = "${var.ENVIRONMENT}-bruin-bridge"
  automation-bruin-bridge-task_definition = "${aws_ecs_task_definition.automation-bruin-bridge.family}:${aws_ecs_task_definition.automation-bruin-bridge.revision}"

  // automation-edge-monitoring-report local vars
  automation-edge-monitoring-report-image = "${data.aws_ecr_repository.automation-edge-monitoring-report.repository_url}:${var.BUILD_NUMBER}"
  automation-edge-monitoring-report-ecs_task_definition-family = "${var.ENVIRONMENT}-edge-monitoring-report"
  automation-edge-monitoring-report-service-security_group-name = "${var.ENVIRONMENT}-edge-monitoring-report"
  automation-edge-monitoring-report_service-resource-name = "${var.ENVIRONMENT}-edge-monitoring-report"
  automation-edge-monitoring-report-service-security_group-tag-Name = "${var.ENVIRONMENT}-edge-monitoring-report"
  automation-edge-monitoring-report-task_definition = "${aws_ecs_task_definition.automation-edge-monitoring-report.family}:${aws_ecs_task_definition.automation-edge-monitoring-report.revision}"

  // automation-last-contact-report local vars
  automation-last-contact-report-ecs_task_definition-family = "${var.ENVIRONMENT}-last-contact-report"
  automation-last-contact-report-image = "${data.aws_ecr_repository.automation-last-contact-report.repository_url}:${var.BUILD_NUMBER}"
  automation-last-contact-report-ecs_task_definition-family = "${var.ENVIRONMENT}-last-contact-report"
  automation-last-contact-report-service-security_group-name = "${var.ENVIRONMENT}-last-contact-report"
  automation-last-contact-report-service-security_group-tag-Name = "${var.ENVIRONMENT}-last-contact-report"
  automation-last-contact-report-resource-name = "${var.ENVIRONMENT}-last-contact-report"
  automation-last-contact-report-task_definition = "${aws_ecs_task_definition.automation-last-contact-report.family}:${aws_ecs_task_definition.automation-last-contact-report.revision}"

  // automation-metrics-grafana local vars
  automation-metrics-grafana-image = "${data.aws_ecr_repository.automation-metrics-grafana.repository_url}:${var.BUILD_NUMBER}"
  automation-metrics-grafana-ecs_task_definition-family = "${var.ENVIRONMENT}-metrics-grafana"
  automation-metrics-grafana-service-security_group-name = "${var.ENVIRONMENT}-metrics-grafana"
  automation-metrics-grafana-service-security_group-tag-Name = "${var.ENVIRONMENT}-metrics-grafana"
  automation-metrics-grafana-ecs_service-name = "${var.ENVIRONMENT}-metrics-grafana"
  automation-metrics-grafana-ecs_task_definition = "${aws_ecs_task_definition.automation-metrics-grafana.family}:${aws_ecs_task_definition.automation-metrics-grafana.revision}"

  // automation-metrics-prometheus local vars
  automation-metrics-prometheus-image = "${data.aws_ecr_repository.automation-metrics-prometheus.repository_url}:${var.BUILD_NUMBER}"
  automation-metrics-prometheus-ecs_task_definition-family = "${var.ENVIRONMENT}-metrics-prometheus"
  automation-metrics-prometheus-service-security_group-name = "${var.ENVIRONMENT}-metrics-prometheus"
  automation-metrics-prometheus-service-security_group-tag-Name = "${var.ENVIRONMENT}-metrics-prometheus"
  automation-metrics-prometheus-ecs_service-name = "${var.ENVIRONMENT}-metrics-prometheus"
  automation-metrics-prometheus-ecs_service-task_definition = "${aws_ecs_task_definition.automation-metrics-prometheus.family}:${aws_ecs_task_definition.automation-metrics-prometheus.revision}"

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

  // automation-service-outage-monitor local vars
  automation-service-outage-monitor-image = "${data.aws_ecr_repository.automation-service-outage-monitor.repository_url}:${var.BUILD_NUMBER}"
  automation-service-outage-monitor-ecs_task_definition-family = "${var.ENVIRONMENT}-service-outage-monitor"
  automation-service-outage-monitor-service-security_group-name = "${var.ENVIRONMENT}-service-outage-monitor"
  automation-service-outage-monitor-service-security_group-tag-Name = "${var.ENVIRONMENT}-service-outage-monitor"
  automation-service-outage-monitor-ecs_service-name = "${var.ENVIRONMENT}-service-outage-monitor"
  automation-service-outage-monitor-ecs_service-task_definition = "${aws_ecs_task_definition.automation-service-outage-monitor.family}:${aws_ecs_task_definition.automation-service-outage-monitor.revision}"

  // automation-service-outage-triage local vars
  automation-service-outage-triage-image = "${data.aws_ecr_repository.automation-service-outage-triage.repository_url}:${var.BUILD_NUMBER}"
  automation-service-outage-triage-log_prefix = "${var.ENVIRONMENT}-${var.BUILD_NUMBER}"
  automation-service-outage-triage-ecs_task_definition-family = "${var.ENVIRONMENT}-service-outage-triage"
  automation-service-outage-triage-service-security_group-name = "${var.ENVIRONMENT}-service-outage-triage"
  automation-service-outage-triage-service-security_group-tag-Name = "${var.ENVIRONMENT}-service-outage-triage"
  automation-service-outage-triage-ecs_service-name = "${var.ENVIRONMENT}-service-outage-triage"
  automation-service-outage-triage-ecs_service-task_definition = "${aws_ecs_task_definition.automation-service-outage-triage.family}:${aws_ecs_task_definition.automation-service-outage-triage.revision}"

  // automation-velocloud-bridge local vars
  automation-velocloud-bridge-image = "${data.aws_ecr_repository.automation-velocloud-bridge.repository_url}:${var.BUILD_NUMBER}"
  automation-velocloud-bridge-log_prefix = "${var.ENVIRONMENT}-${var.BUILD_NUMBER}"
  automation-velocloud-bridge-ecs_task_definition-family = "${var.ENVIRONMENT}-velocloud-bridge"
  automation-velocloud-bridge-service-security_group-tag-Name = "${var.ENVIRONMENT}-velocloud-bridge"
  automation-velocloud-bridge-ecs_service-name = "${var.ENVIRONMENT}-velocloud-bridge"
  automation-velocloud-bridge-ecs_service-task_definition = "${aws_ecs_task_definition.automation-velocloud-bridge.family}:${aws_ecs_task_definition.automation-velocloud-bridge.revision}"

  // automation-velocloud-orchestrator local vars
  automation-velocloud-orchestrator-image = "${data.aws_ecr_repository.automation-velocloud-orchestrator.repository_url}:${var.BUILD_NUMBER}"
  automation-velocloud-orchestrator-log_prefix = "${var.ENVIRONMENT}-${var.BUILD_NUMBER}"
  automation-velocloud-orchestrator-ecs_task_definition-family = "${var.ENVIRONMENT}-velocloud-orchestrator"
  automation-velocloud-orchestrator-service-security_group-name = "${var.ENVIRONMENT}-velocloud-orchestrator"
  automation-velocloud-orchestrator-service-security_group-tag-Name = "${var.ENVIRONMENT}-velocloud-orchestrator"
  automation-velocloud-orchestrator-ecs_service-name = "${var.ENVIRONMENT}-velocloud-orchestrator"
  automation-velocloud-orchestrator-ecs_service-task_definition = "${aws_ecs_task_definition.automation-velocloud-orchestrator.family}:${aws_ecs_task_definition.automation-velocloud-orchestrator.revision}"

}
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

  // automation-service-outage-monitor local vars (for all service-outage-monitor services)
  automation-service-outage-monitor-image = "${data.aws_ecr_repository.automation-service-outage-monitor.repository_url}:${data.external.service-outage-monitor-build_number.result["image_tag"]}"
  automation-service-outage-monitor-velocloud_hosts_triage = ""
  automation-service-outage-monitor-velocloud_hosts_filter = "[]"

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

  // alarm running_task_count_email-tagger-kre-bridge local variables
  running_task_count_email-tagger-kre-bridge_alarm-name = "Running tasks count of email-tagger-kre-bridge service in ECS cluster with name ${var.ENVIRONMENT}"
  running_task_count_email-tagger-kre-bridge_alarm-tag-Name = "${var.ENVIRONMENT}-running_task_count_email-tagger-kre-bridge"

  // alarm running_task_count_email-tagger-monitor local variables
  running_task_count_email-tagger-monitor_alarm-name = "Running tasks count of email-tagger-monitor service in ECS cluster with name ${var.ENVIRONMENT}"
  running_task_count_email-tagger-monitor_alarm-tag-Name = "${var.ENVIRONMENT}-running_task_count_email-tagger-monitor"

  // alarm running_task_count_queue-forwarder local variables
  running_task_count_queue-forwarder_alarm-name = "Running tasks count of queue-forwarder service in ECS cluster with name ${var.ENVIRONMENT}"
  running_task_count_queue-forwarder_alarm-tag-Name = "${var.ENVIRONMENT}-running_task_count_queue-forwarder"

  // cloudformation local variables
  stack_alarms-errors_exceptions_messages_in_services-name = "SnsTopicMetTelAutomationAlarms-${var.ENVIRONMENT}"
  cloudformation_sns_stack_alarms_errors_exceptions_messages-description-stack="MetTel Notificacion Topic for Alarms in ECS cluster with name ${var.ENVIRONMENT}"
  cloudformation_sns_stack_alarms_errors_exceptions_messages-description-operator_email="Email address to notify if there are any active alarms in MetTel automation infrastructure"

}

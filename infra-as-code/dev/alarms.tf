data "template_file" "cloudformation_sns_stack_alarms_erros_exceptions_messages" {
  template = file("${path.module}/cloudformation-templates/mettel_notification_topic_stack.json")
  vars = {
    stack_description = local.cloudformation_sns_stack_alarms_errors_exceptions_messages-description-stack
    operatorEmail_description = local.cloudformation_sns_stack_alarms_errors_exceptions_messages-description-operator_email
  }
}

resource "aws_cloudformation_stack" "sns_topic_alarms" {
  name          = local.stack_alarms-errors_exceptions_messages_in_services-name
  template_body = data.template_file.cloudformation_sns_stack_alarms_erros_exceptions_messages.rendered
  parameters = {
    OperatorEmail = var.ALARMS_SUBSCRIPTIONS_EMAIL_ADDRESS
  }
  tags = {
    Name = local.stack_alarms-errors_exceptions_messages_in_services-name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_sites-monitor_alarm" {
  count = var.sites_monitor_desired_tasks > 0 ? 1 : 0
  alarm_name                = local.running_task_count_sites-monitor_alarm-name
  comparison_operator       = "LessThanOrEqualToThreshold"
  evaluation_periods        = local.running_task_count_service-alarm-evaluation_periods
  metric_name               = local.running_task_count-metric_transformation-name
  namespace                 = "ECS/ContainerInsights"
  period                    = local.running_task_count_service-alarm-period
  statistic                 = "Sum"
  threshold                 = local.running_task_count_service-alarm-threshold * var.sites_monitor_desired_tasks
  insufficient_data_actions = []
  alarm_description         = "This metric monitors the number of running tasks of sites-monitor service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions             = [ aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"] ]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-sites-monitor"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_sites-monitor_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_tnba-monitor_alarm" {
  count = var.tnba_monitor_desired_tasks > 0 ? 1 : 0
  alarm_name                = local.running_task_count_tnba-monitor_alarm-name
  comparison_operator       = "LessThanOrEqualToThreshold"
  evaluation_periods        = local.running_task_count_service-alarm-evaluation_periods
  metric_name               = local.running_task_count-metric_transformation-name
  namespace                 = "ECS/ContainerInsights"
  period                    = local.running_task_count_service-alarm-period
  statistic                 = "Sum"
  threshold                 = local.running_task_count_service-alarm-threshold
  insufficient_data_actions = []
  alarm_description         = "This metric monitors the number of running tasks of tnba-monitor service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions             = [ aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"] ]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-tnba-monitor"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_tnba-monitor_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}


resource "aws_cloudwatch_metric_alarm" "running_task_count_bruin-bridge_alarm" {
  count = var.bruin_bridge_desired_tasks > 0 ? 1 : 0
  alarm_name                = local.running_task_count_bruin-bridge_alarm-name
  comparison_operator       = "LessThanOrEqualToThreshold"
  evaluation_periods        = local.running_task_count_service-alarm-evaluation_periods
  metric_name               = local.running_task_count-metric_transformation-name
  namespace                 = "ECS/ContainerInsights"
  period                    = local.running_task_count_service-alarm-period
  statistic                 = "Sum"
  threshold                 = local.running_task_count_service-alarm-threshold * var.bruin_bridge_desired_tasks
  insufficient_data_actions = []
  alarm_description         = "This metric monitors the number of running tasks of bruin-bridge service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions             = [ aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"] ]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-bruin-bridge"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_bruin-bridge_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_service-affecting-monitor_alarm" {
  count = var.service_affecting_monitor_desired_tasks > 0 ? 1 : 0
  alarm_name = local.running_task_count_service-affecting-monitor_alarm-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold * var.service_affecting_monitor_desired_tasks
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of service-affecting-monitor service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-service-affecting-monitor"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_service-affecting-monitor_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_t7-bridge_alarm" {
  count = var.t7_bridge_desired_tasks > 0 ? 1 : 0
  alarm_name = local.running_task_count_t7-bridge_alarm-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold * var.t7_bridge_desired_tasks
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of t7-bridge service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-t7-bridge"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_t7-bridge_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_notifier_alarm" {
  count = var.notifier_desired_tasks > 0 ? 1 : 0
  alarm_name = local.running_task_count_notifier_alarm-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold * var.notifier_desired_tasks
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of notifier service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-notifier"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_notifier_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_metrics-prometheus_alarm" {
  count = var.metrics_prometheus_desired_tasks > 0 ? 1 : 0
  alarm_name = local.running_task_count_metrics-prometheus_alarm-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold * var.metrics_prometheus_desired_tasks
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of metrics-prometheus service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-metrics-prometheus"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_metrics-prometheus_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_nats-server_alarm" {
  count = var.nats_server_desired_tasks > 0 ? 1 : 0
  alarm_name = local.running_task_count_nats-server_alarm-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold * var.nats_server_desired_tasks
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of nats-server service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-nats-server"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_nats-server_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_nats-server-1_alarm" {
  count = var.nats_server_1_desired_tasks > 0 ? 1 : 0
  alarm_name = local.running_task_count_nats-server-1_alarm-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold * var.nats_server_1_desired_tasks
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of nats-server-1 service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-nats-server-1"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_nats-server-1_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_nats-server-2_alarm" {
  count = var.nats_server_2_desired_tasks > 0 ? 1 : 0
  alarm_name = local.running_task_count_nats-server-2_alarm-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold * var.nats_server_2_desired_tasks
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of nats-server-2 service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-nats-server-2"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_nats-server-2_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_service-dispatch_monitor_alarm" {
  count = var.service_dispatch_monitor_desired_tasks > 0 ? 1 : 0
  alarm_name = local.running_task_count_service-dispatch-monitor_alarm-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold * var.service_dispatch_monitor_desired_tasks
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of service-dispatch-monitor service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-service-dispatch-monitor"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_service-dispatch-monitor_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_service-outage-monitor-1_alarm" {
  count = var.service_outage_monitor_1_desired_tasks > 0 ? 1 : 0
  alarm_name = local.running_task_count_service-outage-monitor-1_alarm-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold * var.service_outage_monitor_1_desired_tasks
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of service-outage-monitor-1 service for Velocloud host# 1 in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-service-outage-monitor-1"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_service-outage-monitor-1_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_service-outage-monitor-2_alarm" {
  count = var.service_outage_monitor_2_desired_tasks > 0 ? 1 : 0
  alarm_name = local.running_task_count_service-outage-monitor-2_alarm-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold * var.service_outage_monitor_2_desired_tasks
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of service-outage-monitor-2 service for Velocloud host# 1 in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-service-outage-monitor-2"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_service-outage-monitor-2_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_service-outage-monitor-3_alarm" {
  count = var.service_outage_monitor_3_desired_tasks > 0 ? 1 : 0
  alarm_name = local.running_task_count_service-outage-monitor-3_alarm-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold * var.service_outage_monitor_3_desired_tasks
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of service-outage-monitor-3 service for Velocloud host# 1 in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-service-outage-monitor-3"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_service-outage-monitor-3_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_service-outage-monitor-4_alarm" {
  count = var.service_outage_monitor_4_desired_tasks > 0 ? 1 : 0
  alarm_name = local.running_task_count_service-outage-monitor-4_alarm-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold * var.service_outage_monitor_4_desired_tasks
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of service-outage-monitor-4 service for Velocloud host# 1 in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-service-outage-monitor-4"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_service-outage-monitor-4_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_service-outage-monitor-triage_alarm" {
  count = var.service_outage_monitor_triage_desired_tasks > 0 ? 1 : 0
  alarm_name = local.running_task_count_service-outage-monitor-triage_alarm-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold * var.service_outage_monitor_triage_desired_tasks
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of service-outage-monitor service for Velocloud host# 1 in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-service-outage-monitor-triage"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_service-outage-monitor-triage_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_last-contact-report_alarm" {
  count = var.last_contact_report_desired_tasks > 0 ? 1 : 0
  alarm_name = local.running_task_count_last-contact-report_alarm-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold * var.last_contact_report_desired_tasks
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of last-contact-report service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-last-contact-report"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_last-contact-report_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_lumin-billing-report_alarm" {
  count = var.lumin_billing_report_desired_tasks > 0 ? 1 : 0
  alarm_name = local.running_task_count_lumin-billing-report_alarm-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold * var.lumin_billing_report_desired_tasks
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of lumin-billing-report service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-lumin-billing-report"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_lumin-billing-report_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_velocloud-bridge_alarm" {
  count = var.velocloud_bridge_desired_tasks > 0 ? 1 : 0
  alarm_name = local.running_task_count_velocloud-bridge_alarm-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold * var.velocloud_bridge_desired_tasks
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of velocloud-bridge service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-velocloud-bridge"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_velocloud-bridge_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_cts-bridge_alarm" {
  count = var.cts_bridge_desired_tasks > 0 ? 1 : 0
  alarm_name = local.running_task_count_cts-bridge_alarm-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold * var.cts_bridge_desired_tasks
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of cts-bridge service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-cts-bridge"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_cts-bridge_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_dispatch-portal-frontend_alarm" {
  count = var.dispatch_portal_frontend_desired_tasks > 0 ? 1 : 0
  alarm_name = local.running_task_count_dispatch-portal-frontend_alarm-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold * var.dispatch_portal_frontend_desired_tasks
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of dispatch-portal-frontend service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-dispatch-portal-frontend"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_dispatch-portal-frontend_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_dispatch-portal-backend_alarm" {
  count = var.dispatch_portal_backend_desired_tasks > 0 ? 1 : 0
  alarm_name = local.running_task_count_dispatch-portal-backend_alarm-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold * var.dispatch_portal_backend_desired_tasks
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of dispatch-portal-backend service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-dispatch-portal-backend"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_dispatch-portal-backend_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_customer-cache_alarm" {
  count = var.customer_cache_desired_tasks > 0 ? 1 : 0
  alarm_name = local.running_task_count_customer-cache_alarm-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold * var.customer_cache_desired_tasks
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of customer-cache service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-customer-cache"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_customer-cache_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_hawkeye-customer-cache_alarm" {
  count = var.hawkeye_customer_cache_desired_tasks > 0 ? 1 : 0
  alarm_name = local.running_task_count_hawkeye-customer-cache_alarm-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold * var.hawkeye_customer_cache_desired_tasks
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of hawkeye-customer-cache service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-hawkeye-customer-cache"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_hawkeye-customer-cache_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_tnba-feedback_alarm" {
  count = var.tnba_feedback_desired_tasks > 0 ? 1 : 0
  alarm_name = local.running_task_count_tnba-feedback_alarm-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold * var.tnba_feedback_desired_tasks
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of tnba-feedback service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-tnba-feedback"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_tnba-feedback_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_hawkeye-bridge_alarm" {
  count = var.hawkeye_bridge_desired_tasks > 0 ? 1 : 0
  alarm_name                = local.running_task_count_hawkeye-bridge_alarm-name
  comparison_operator       = "LessThanOrEqualToThreshold"
  evaluation_periods        = local.running_task_count_service-alarm-evaluation_periods
  metric_name               = local.running_task_count-metric_transformation-name
  namespace                 = "ECS/ContainerInsights"
  period                    = local.running_task_count_service-alarm-period
  statistic                 = "Sum"
  threshold                 = local.running_task_count_service-alarm-threshold * var.hawkeye_bridge_desired_tasks
  insufficient_data_actions = []
  alarm_description         = "This metric monitors the number of running tasks of hawkeye-bridge service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions             = [ aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"] ]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-hawkeye-bridge"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_hawkeye-bridge_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_hawkeye-outage-monitor_alarm" {
  count = var.hawkeye_outage_monitor_desired_tasks > 0 ? 1 : 0
  alarm_name = local.running_task_count_hawkeye-outage-monitor_alarm-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold * var.hawkeye_outage_monitor_desired_tasks
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of hawkeye-outage-monitor service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-hawkeye-outage-monitor"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_hawkeye-outage-monitor_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}
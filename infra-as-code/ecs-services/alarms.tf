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
    OperatorEmail = var.alarms_subscriptions_email_addresses
  }
  tags = merge(
    map("Name", local.stack_alarms-errors_exceptions_messages_in_services-name)
  )
}

resource "aws_cloudwatch_metric_alarm" "exception_messages_services_alarm" {
  alarm_name                = local.exception_messages_services_alarm-name
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = local.exception_messages_services_alarm-evaluation_periods
  metric_name               = local.exceptions_detected_metric-metric_transformation-name
  namespace                 = "LogMetrics"
  period                    = local.exception_messages_services_alarm-period
  statistic                 = "Sum"
  threshold                 = local.exception_messages_services_alarm-threshold
  insufficient_data_actions = []
  alarm_description         = "This metric monitors number of exception messages for all the services in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions             = [ aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"] ]
}

resource "aws_cloudwatch_metric_alarm" "error_messages_services_alarm" {
  alarm_name                = local.error_messages_services_alarm-name
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = local.error_messages_services_alarm-evaluation_periods
  metric_name               = local.errors_detected_metric-metric_transformation-name
  namespace                 = "LogMetrics"
  period                    = local.error_messages_services_alarm-period
  statistic                 = "Sum"
  threshold                 = local.error_messages_services_alarm-threshold
  insufficient_data_actions = []
  alarm_description         = "This metric monitors number of error messages for all the services in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions             = [ aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"] ]
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_velocloud-orchestrator_alarm" {
  alarm_name                = local.running_task_count_velocloud-orchestator_alarm-name
  comparison_operator       = "LessThanOrEqualToThreshold"
  evaluation_periods        = local.running_task_count_service-alarm-evaluation_periods
  metric_name               = local.running_task_count-metric_transformation-name
  namespace                 = "ECS/ContainerInsights"
  period                    = local.running_task_count_service-alarm-period
  statistic                 = "Sum"
  threshold                 = local.running_task_count_service-alarm-threshold
  insufficient_data_actions = []
  alarm_description         = "This metric monitors the number of running tasks of velocloud-orchestrator service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions             = [ aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"] ]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-velocloud-orchestrator"
    ClusterName = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_bruin-bridge_alarm" {
  alarm_name                = local.running_task_count_bruin-bridge_alarm-name
  comparison_operator       = "LessThanOrEqualToThreshold"
  evaluation_periods        = local.running_task_count_service-alarm-evaluation_periods
  metric_name               = local.running_task_count-metric_transformation-name
  namespace                 = "ECS/ContainerInsights"
  period                    = local.running_task_count_service-alarm-period
  statistic                 = "Sum"
  threshold                 = local.running_task_count_service-alarm-threshold
  insufficient_data_actions = []
  alarm_description         = "This metric monitors the number of running tasks of bruin-bridge service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions             = [ aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"] ]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-bruin-bridge"
    ClusterName = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_service-outage-triage_alarm" {
  alarm_name                = local.running_task_count_service-outage-triage_alarm-name
  comparison_operator       = "LessThanOrEqualToThreshold"
  evaluation_periods        = local.running_task_count_service-alarm-evaluation_periods
  metric_name               = local.running_task_count-metric_transformation-name
  namespace                 = "ECS/ContainerInsights"
  period                    = local.running_task_count_service-alarm-period
  statistic                 = "Sum"
  threshold                 = local.running_task_count_service-alarm-threshold
  insufficient_data_actions = []
  alarm_description         = "This metric monitors the number of running tasks of service-outage-triage service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions             = [ aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"] ]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-service-outage-triage"
    ClusterName = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_service-affecting-monitor_alarm" {
  alarm_name = local.running_task_count_service-affecting-monitor_alarm-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of service-affecting-monitor service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-service-affecting-monitor"
    ClusterName = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_t7-bridge_alarm" {
  alarm_name = local.running_task_count_t7-bridge-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of t7-bridge service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-t7-bridge"
    ClusterName = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_notifier_alarm" {
  alarm_name = local.running_task_count_notifier-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of notifier service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-notifier"
    ClusterName = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_metrics-grafana_alarm" {
  alarm_name = local.running_task_count_metrics-grafana-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of metrics-grafana service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-metrics-grafana"
    ClusterName = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_metrics-prometheus_alarm" {
  alarm_name = local.running_task_count_metrics-prometheus-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of metrics-prometheus service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-metrics-prometheus"
    ClusterName = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_nats-server_alarm" {
  alarm_name = local.running_task_count_nats-server-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of nats-server service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-nats-server"
    ClusterName = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_service-outage-monitor_alarm" {
  alarm_name = local.running_task_count_service-outage-monitor-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of service-outage-monitor service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-service-outage-monitor"
    ClusterName = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_last-contact-report_alarm" {
  alarm_name = local.running_task_count_last-contact-report-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of last-contact-report service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-last-contact-report"
    ClusterName = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_velocloud-bridge_alarm" {
  alarm_name = local.running_task_count_velocloud-bridge-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of velocloud-bridge service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-velocloud-bridge"
    ClusterName = var.ENVIRONMENT
  }
}
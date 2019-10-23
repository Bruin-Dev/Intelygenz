data "template_file" "cloudformation_sns_stack_alarms_erros_exceptions_messages" {
  template = file("${path.module}/cloudformation-templates/mettel_notification_topic_stack.json")
  vars = {
    stack_description = local.cloudformation_sns_stack_alarms_errors_exceptions_messages-description-stack
    operatorEmail_description = local.cloudformation_sns_stack_alarms_errors_exceptions_messages-description-operator_email
  }
}

resource "aws_cloudformation_stack" "sns_topic_alarm_errors_exceptions_services" {
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
  evaluation_periods        = "1"
  metric_name               = local.exceptions_detected_metric-metric_transformation-name
  namespace                 = "LogMetrics"
  period                    = "120"
  statistic                 = "Sum"
  threshold                 = "5"
  insufficient_data_actions = []
  alarm_description         = "This metric monitors number of exception messages for all the services in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions             = [ aws_cloudformation_stack.sns_topic_alarm_errors_exceptions_services.outputs["TopicARN"] ]
}

resource "aws_cloudwatch_metric_alarm" "error_messages_services_alarm" {
  alarm_name                = local.error_messages_services_alarm-name
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = "1"
  metric_name               = local.errors_detected_metric-metric_transformation-name
  namespace                 = "LogMetrics"
  period                    = "120"
  statistic                 = "Sum"
  threshold                 = "5"
  insufficient_data_actions = []
  alarm_description         = "This metric monitors number of error messages for all the services in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions             = [ aws_cloudformation_stack.sns_topic_alarm_errors_exceptions_services.outputs["TopicARN"] ]
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_velocloud-orchestator_alarm" {
  alarm_name                = local.running_task_count_velocloud-orchestator_alarm-name
  comparison_operator       = "LessThanOrEqualToThreshold"
  evaluation_periods        = "1"
  metric_name               = local.running_task_count-metric_transformation-name
  namespace                 = "ECS/ContainerInsights"
  period                    = "300"
  statistic                 = "Sum"
  threshold                 = "3"
  insufficient_data_actions = []
  alarm_description         = "This metric monitors the number of running tasks of velocloud-orchestrator service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions             = [ aws_cloudformation_stack.sns_topic_alarm_errors_exceptions_services.outputs["TopicARN"] ]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-velocloud-orchestrator"
    ClusterName = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_bruin-bridge_alarm" {
  alarm_name                = local.running_task_count_bruin-bridge_alarm-name
  comparison_operator       = "LessThanOrEqualToThreshold"
  evaluation_periods        = "1"
  metric_name               = local.running_task_count-metric_transformation-name
  namespace                 = "ECS/ContainerInsights"
  period                    = "300"
  statistic                 = "Sum"
  threshold                 = "3"
  insufficient_data_actions = []
  alarm_description         = "This metric monitors the number of running tasks of bruin-bridge service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions             = [ aws_cloudformation_stack.sns_topic_alarm_errors_exceptions_services.outputs["TopicARN"] ]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-bruin-bridge"
    ClusterName = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_service-outage-triage_alarm" {
  alarm_name                = local.running_task_count_service-outage-triage_alarm-name
  comparison_operator       = "LessThanOrEqualToThreshold"
  evaluation_periods        = "1"
  metric_name               = local.running_task_count-metric_transformation-name
  namespace                 = "ECS/ContainerInsights"
  period                    = "300"
  statistic                 = "Sum"
  threshold                 = "3"
  insufficient_data_actions = []
  alarm_description         = "This metric monitors the number of running tasks of service-outage-triage service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions             = [ aws_cloudformation_stack.sns_topic_alarm_errors_exceptions_services.outputs["TopicARN"] ]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-service-outage-triage"
    ClusterName = var.ENVIRONMENT
  }
}
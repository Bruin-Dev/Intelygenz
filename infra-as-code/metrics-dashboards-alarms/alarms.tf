data "template_file" "cloudformation_sns_stack_alarms" {
  template = file("${path.module}/cloudformation-templates/mettel_notification_topic_stack.json")
}

resource "aws_cloudformation_stack" "sns_topic_alarm" {
  name          = local.stack_alarms-name
  template_body = data.template_file.cloudformation_sns_stack_alarms.rendered
  tags = merge(
    map("Name", local.stack_alarms-name)
  )
}

output "arn" {
  value       = aws_cloudformation_stack.sns_topic_alarm.outputs["ARN"]
  description = "Email SNS topic ARN"
}

resource "aws_cloudwatch_metric_alarm" "errors_messages_services_alarm" {
  alarm_name                = local.cluster_task_running-alarm_name
  comparison_operator       = "LessThanThreshold"
  evaluation_periods        = "2"
  metric_name               = local.exception_detected_metric-metric_transformation-name
  namespace                 = "LogMetrics"
  period                    = "120"
  statistic                 = "Sum"
  threshold                 = "5"
  alarm_description         = "This metric monitors number of message errors for all the services in the cluster"
  insufficient_data_actions = []
  alarm_actions     = [ aws_cloudformation_stack.sns_topic_alarm.outputs["NotificationTopic"] ]
  #depends_on = [aws_cloudformation_stack.sns_topic_alarm]
}
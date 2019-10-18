data "aws_cloudwatch_log_group" "log_group_automation" {
  name = var.ENVIRONMENT
}

resource "aws_cloudwatch_log_metric_filter" "errors_detected_metric" {
  name           = "Erros_messages_detected_in_services"
  pattern        = ": ERROR"
  log_group_name = data.aws_cloudwatch_log_group.log_group_automation.name

  metric_transformation {
    name      = "ErrorsMessagesDetectedInServices "
    namespace = "LogMetrics"
    value     = "1"
    default_value = "0"
  }
}

resource "aws_cloudwatch_log_metric_filter" "exception_detected_metric" {
  name           = "Exception_messages_detected_in_services"
  pattern        = "Exception"
  log_group_name = data.aws_cloudwatch_log_group.log_group_automation.name

  metric_transformation {
    name      = "ExceptionMessagesDetectedInServices "
    namespace = "LogMetrics"
    value     = "1"
    default_value = "0"
  }
}
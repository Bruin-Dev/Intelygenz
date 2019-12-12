resource "aws_cloudwatch_log_metric_filter" "errors_detected_metric" {
  name           = "Errors_messages_detected_in_services-ECS_cluster_${var.ENVIRONMENT}"
  pattern        = "\": ERROR\""
  log_group_name = aws_cloudwatch_log_group.automation.name

  metric_transformation {
    name      = local.errors_detected_metric-metric_transformation-name
    namespace = "LogMetrics"
    value     = "1"
    default_value = "0"
  }
}

resource "aws_cloudwatch_log_metric_filter" "exception_detected_metric" {
  name           = "Exception_messages_detected_in_services-ECS_cluster_${var.ENVIRONMENT}"
  pattern        = "Exception"
  log_group_name = aws_cloudwatch_log_group.automation.name

  metric_transformation {
    name      = local.exceptions_detected_metric-metric_transformation-name
    namespace = "LogMetrics"
    value     = "1"
    default_value = "0"
  }
}
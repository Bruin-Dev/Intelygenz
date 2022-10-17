resource "aws_cloudwatch_log_metric_filter" "servicenow_bridge__error" {
  name           = "servicenow_bridge__error"
  pattern        = "{ $.environment = \"production\" && $.hostname = \"servicenow-bridge-*\" && $.log_level = \"ERROR\" }"
  log_group_name = data.aws_cloudwatch_log_group.eks_log_group.name

  metric_transformation {
    name      = "servicenow_bridge__error"
    namespace = "mettel_automation/alarms"
    value     = "1"
  }
}

resource "aws_cloudwatch_metric_alarm" "servicenow-bridge-too-many-errors" {
  alarm_name                = "servicenow-bridge-too-many-errors"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = "1"
  metric_name               = aws_cloudwatch_log_metric_filter.servicenow_bridge__error.name
  namespace                 = "mettel_automation/alarms"
  period                    = "3600"
  statistic                 = "Sum"
  threshold                 = "100"
  alarm_description         = "Triggers an alarm if the ServiceNow Bridge reported too many errors"
  insufficient_data_actions = []
alarm_actions = []
}

resource "aws_sns_topic" "servicenow-bridge-too-many-errors" {
  name = "servicenow-bridge-too-many-errors"
}

resource "aws_sns_topic_subscription" "servicenow-bridge-too-many-errors"{
  for_each  = toset(["mettel.team@intelygenz.com"])
  topic_arn = aws_sns_topic.servicenow-bridge-too-many-errors.arn
  protocol = "email"
  endpoint = each.value
}
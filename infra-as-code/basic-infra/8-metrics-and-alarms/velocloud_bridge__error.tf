resource "aws_cloudwatch_log_metric_filter" "velocloud_bridge__error" {
  name           = "velocloud_bridge__error"
  pattern        = "{ $.environment = \"production\" && $.hostname = \"velocloud-bridge-*\" && $.log_level = \"ERROR\" }"
  log_group_name = aws_cloudwatch_log_group.eks_log_group.name

  metric_transformation {
    name      = "velocloud_bridge__error"
    namespace = "mettel_automation/alarms"
    value     = "$.message"
  }
}

resource "aws_cloudwatch_metric_alarm" "bruin-bridge-too-many-errors-in-the-last-hour" {
  alarm_name                = "bruin-bridge-too-many-errors-in-the-last-hour"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = "1"
  metric_name               = aws_cloudwatch_log_metric_filter.velocloud_bridge__error.name
  namespace                 = "mettel_automation/alarms"
  period                    = "3600"
  statistic                 = "Sum"
  threshold                 = "300"
  alarm_description         = "Triggers an alarm if the Velocloud Bridge reported too many errors in the last hour"
  insufficient_data_actions = []
alarm_actions = []
}

resource "aws_sns_topic" "bruin-bridge-too-many-errors-in-the-last-hour" {
  name = "bruin-bridge-too-many-errors-in-the-last-hour"
}

resource "aws_sns_topic_subscription" "bruin-bridge-too-many-errors-in-the-last-hour"{
  for_each  = toset(["mettel.team@intelygenz.com"])
  topic_arn = aws_sns_topic.bruin-bridge-too-many-errors-in-the-last-hour.arn
  protocol = "email"
  endpoint = each.value
}
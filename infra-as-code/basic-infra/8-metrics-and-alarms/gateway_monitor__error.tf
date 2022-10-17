resource "aws_cloudwatch_log_metric_filter" "gateway_monitor__error" {
  name           = "gateway_monitor__error"
  pattern        = "{ $.environment = \"production\" && $.hostname = \"gateway-monitor-*\" && $.log_level = \"ERROR\" }"
  log_group_name = aws_cloudwatch_log_group.eks_log_group.name

  metric_transformation {
    name      = "gateway_monitor__error"
    namespace = "mettel_automation/alarms"
    value     = "1"
  }
}

resource "aws_cloudwatch_metric_alarm" "velocloud-gateways-too-many-errors-in-the-last-hour" {
  alarm_name                = "velocloud-gateways-too-many-errors-in-the-last-hour"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = "1"
  metric_name               = aws_cloudwatch_log_metric_filter.gateway_monitor__error.name
  namespace                 = "mettel_automation/alarms"
  period                    = "3600"
  statistic                 = "Sum"
  threshold                 = "100"
  alarm_description         = "Triggers an alarm if the ServiceNow Bridge reported too many errors in the last hour"
  insufficient_data_actions = []
alarm_actions = []
}

resource "aws_sns_topic" "velocloud-gateways-too-many-errors-in-the-last-hour" {
  name = "velocloud-gateways-too-many-errors-in-the-last-hour"
}

resource "aws_sns_topic_subscription" "velocloud-gateways-too-many-errors-in-the-last-hour"{
  for_each  = toset(["mettel.team@intelygenz.com"])
  topic_arn = aws_sns_topic.velocloud-gateways-too-many-errors-in-the-last-hour.arn
  protocol = "email"
  endpoint = each.value
}
resource "aws_cloudwatch_log_metric_filter" "intermapper_outage__down_events_received" {
  name           = "intermapper_outage__down_events_received"
  pattern        = "{ $.environment = \"production\" && $.hostname = \"intermapper-outage-monitor-*\" && $.message = \"Event from InterMapper was *. Checking for ticket creation*\" }"
  log_group_name = aws_cloudwatch_log_group.eks_log_group.name

  metric_transformation {
    name      = "intermapper_outage__down_events_received"
    namespace = "mettel_automation/alarms"
    value     = "$.message"
  }
}

resource "aws_cloudwatch_metric_alarm" "intermapper-outage-too-many-down-events-in-the-last-10-minutes" {
  alarm_name                = "intermapper-outage-too-many-down-events-in-the-last-10-minutes"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = "1"
  metric_name               = aws_cloudwatch_log_metric_filter.intermapper_outage__down_events_received.name
  namespace                 = "mettel_automation/alarms"
  period                    = "600"
  statistic                 = "Sum"
  threshold                 = "100"
  alarm_description         = "Triggers an alarm if a fixed number of InterMapper down events received in the last 10 minutes is exceeded"
  insufficient_data_actions = []
alarm_actions = []
}

resource "aws_sns_topic" "[TBD]" {
  name = "[TBD]"
}

resource "aws_sns_topic_subscription" "[TBD]"{
  for_each  = toset(["managedservices@mettel.net", "ndimuro@mettel.net", "bsullivan@mettel.net", "mettel.team@intelygenz.com"])
  topic_arn = aws_sns_topic.TBD.arn
  protocol = "email"
  endpoint = each.value
}

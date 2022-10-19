resource "aws_cloudwatch_log_metric_filter" "intermapper_outage__down_events_received" {
  name           = "intermapper_outage__down_events_received"
  pattern        = "{ $.environment = \"production\" && $.hostname = \"intermapper-outage-monitor-*\" && $.message = \"Event from InterMapper was *. Checking for ticket creation*\" }"
  log_group_name = data.aws_cloudwatch_log_group.eks_log_group.name

  metric_transformation {
    name      = "intermapper_outage__down_events_received"
    namespace = "mettel_automation/alarms"
    value     = "1"
  }
}

resource "aws_cloudwatch_metric_alarm" "intermapper-outage-too-many-down-events" {
  alarm_name                = "intermapper-outage-too-many-down-events"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = "1"
  metric_name               = aws_cloudwatch_log_metric_filter.intermapper_outage__down_events_received.name
  namespace                 = "mettel_automation/alarms"
  period                    = "3600"
  statistic                 = "Sum"
  threshold                 = "100"
  alarm_description         = "Triggers an alarm if a fixed number of InterMapper down events received is exceeded"
  insufficient_data_actions = []
  actions_enabled           = "true"
  alarm_actions             = [aws_sns_topic.intermapper-outage-too-many-down-events.arn]
}

resource "aws_sns_topic" "intermapper-outage-too-many-down-events" {
  name = "intermapper-outage-too-many-down-events"
}

resource "aws_sns_topic_subscription" "intermapper-outage-too-many-down-events"{
  for_each  = toset(["managedservices@mettel.net", "ndimuro@mettel.net", "bsullivan@mettel.net", "mettel.team@intelygenz.com"])
  topic_arn = aws_sns_topic.intermapper-outage-too-many-down-events.arn
  protocol  = "email"
  endpoint  = each.value
}

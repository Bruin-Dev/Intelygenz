resource "aws_cloudwatch_log_metric_filter" "intermapper_outage__events_processed" {
  name           = "intermapper_outage__events_processed"
  pattern        = "{ $.environment = \"production\" && $.hostname = \"intermapper-outage-monitor-*\" && $.message = \"Processing email with msg_uid:\" }"
  log_group_name = aws_cloudwatch_log_group.eks_log_group.name

  metric_transformation {
    name      = "intermapper_outage__events_processed"
    namespace = "mettel_automation/alarms"
    value     = "1"
  }
}

resource "aws_cloudwatch_metric_alarm" "intermapper-outage-no-events-processed-in-the-last-hour" {
  alarm_name                = "intermapper-outage-no-events-processed-in-the-last-hour"
  comparison_operator       = "LowerThanOrEqualToThreshold"
  evaluation_periods        = "1"
  metric_name               = aws_cloudwatch_log_metric_filter.intermapper_outage__events_processed.name
  namespace                 = "mettel_automation/alarms"
  period                    = "3600"
  statistic                 = "Sum"
  threshold                 = "0"
  alarm_description         = "Triggers an alarm if no emails get into the inbox in the last 10 minutes"
  insufficient_data_actions = []
alarm_actions = []
}

resource "aws_sns_topic" "intermapper-outage-no-events-processed-in-the-last-hour" {
  name = "intermapper-outage-no-events-processed-in-the-last-hour"
}

resource "aws_sns_topic_subscription" "intermapper-outage-no-events-processed-in-the-last-hour"{
  for_each  = toset(["mettel.team@intelygenz.com"])
  topic_arn = aws_sns_topic.intermapper-outage-no-events-processed-in-the-last-hour.arn
  protocol = "email"
  endpoint = each.value
}
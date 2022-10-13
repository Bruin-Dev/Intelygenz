resource "aws_cloudwatch_log_metric_filter" "intermapper_outage__events_processed" {
  name           = "intermapper_outage__events_processed"
  pattern        = "{ $.environment = \"production\" && $.hostname = \"email-bridge-*\" && $.message = \"There was an error trying to login into the inbox*\" }"
  log_group_name = aws_cloudwatch_log_group.eks_log_group.name

  metric_transformation {
    name      = "intermapper_outage__events_processed"
    namespace = "mettel_automation/alarms"
    value     = "$.message"
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
  alarm_description         = "Triggers an alarm if no InterMapper events were processed in the last hour"
  insufficient_data_actions = []
alarm_actions = []
}

resource "aws_sns_topic" "intermapper-outage-no-events-processed-in-the-last-hou" {
  name = "intermapper-outage-no-events-processed-in-the-last-hou"
}

resource "aws_sns_topic_subscription" "intermapper-outage-no-events-processed-in-the-last-hou"{
  for_each  = toset(["mettel.team@intelygenz.com"])
  topic_arn = aws_sns_topic.intermapper-outage-no-events-processed-in-the-last-hou.arn
  protocol = "email"
  endpoint = each.value
}
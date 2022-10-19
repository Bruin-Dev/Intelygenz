resource "aws_cloudwatch_log_metric_filter" "intermapper_outage__events_processed" {
  name           = "intermapper_outage__events_processed"
  pattern        = "{ $.log=\"*production*intermapper-outage*Processing email with msg_uid:*\"}"
  log_group_name = data.aws_cloudwatch_log_group.eks_log_group.name

  metric_transformation {
    name      = "intermapper_outage__events_processed"
    namespace = "mettel_automation/alarms"
    value     = "1"
  }
}

resource "aws_cloudwatch_metric_alarm" "intermapper-outage-no-events-processed" {
  alarm_name                = "intermapper-outage-no-events-processed"
  comparison_operator       = "LessThanOrEqualToThreshold"
  evaluation_periods        = "1"
  metric_name               = aws_cloudwatch_log_metric_filter.intermapper_outage__events_processed.name
  namespace                 = "mettel_automation/alarms"
  period                    = "3600"
  statistic                 = "Sum"
  threshold                 = "0"
  alarm_description         = "Triggers an alarm if no emails get into the inbox"
  insufficient_data_actions = []
  actions_enabled           = "true"
  alarm_actions             = [aws_sns_topic.intermapper-outage-no-events-processed.arn]
}

resource "aws_sns_topic" "intermapper-outage-no-events-processed" {
  name = "intermapper-outage-no-events-processed"
}

resource "aws_sns_topic_subscription" "intermapper-outage-no-events-processed"{
  for_each  = toset(["mettel.team@intelygenz.com"])
  topic_arn = aws_sns_topic.intermapper-outage-no-events-processed.arn
  protocol = "email"
  endpoint = each.value
}
resource "aws_cloudwatch_log_metric_filter" "intermapper_outage__no_emails_received" {
  name           = "intermapper_outage__no_emails_received"
  pattern        = "{ $.environment = \"production\" && $.hostname = \"intermapper-outage-monitor-*\" && $.message = \"Received the following from the gmail account mettel.automation@intelygenz.com: []\" }"
  log_group_name = data.aws_cloudwatch_log_group.eks_log_group.name

  metric_transformation {
    name      = "intermapper_outage__no_emails_received"
    namespace = "mettel_automation/alarms"
    value     = "1"
  }
}

resource "aws_cloudwatch_metric_alarm" "intermapper-outage-no-emails-received" {
  alarm_name                = "intermapper-outage-no-emails-received"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = "1"
  metric_name               = aws_cloudwatch_log_metric_filter.intermapper_outage__no_emails_received.name
  namespace                 = "mettel_automation/alarms"
  period                    = "1800"
  statistic                 = "Sum"
  threshold                 = "50"
  alarm_description         = "Triggers an alarm if no emails get into the inbox"
  insufficient_data_actions = []
  actions_enabled           = "true"
  alarm_actions             = [aws_sns_topic.intermapper-outage-no-emails-received.arn]
}

resource "aws_sns_topic" "intermapper-outage-no-emails-received" {
  name = "intermapper-outage-no-emails-received"
}

resource "aws_sns_topic_subscription" "intermapper-outage-no-emails-received" {
  for_each  = toset(["managedservices@mettel.net", "ndimuro@mettel.net", "bsullivan@mettel.net", "jhicks@mettel.net", "mettel.team@intelygenz.com"])
  topic_arn = aws_sns_topic.intermapper-outage-no-emails-received.arn
  protocol  = "email"
  endpoint  = each.value
}

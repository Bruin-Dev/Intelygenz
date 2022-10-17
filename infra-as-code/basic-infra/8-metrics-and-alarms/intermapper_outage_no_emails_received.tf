resource "aws_cloudwatch_log_metric_filter" "intermapper_outage__no_emails_received" {
  name           = "intermapper_outage__no_emails_received"
  pattern        = "{ $.environment = \"production\" && $.hostname = \"intermapper-outage-monitor-*\" && $.message = \"Received the following from the gmail account mettel.automation@intelygenz.com: []\" }"
  log_group_name = aws_cloudwatch_log_group.eks_log_group.name

  metric_transformation {
    name      = "intermapper_outage__no_emails_received"
    namespace = "mettel_automation/alarms"
    value     = "1"
  }
}

resource "aws_cloudwatch_metric_alarm" "intermapper-outage-no-emails-received-in-the-last-10-minutes" {
  alarm_name                = "bruin-too-many-invalid-service-outage-ticket-creations"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = "1"
  metric_name               = aws_cloudwatch_log_metric_filter.intermapper_outage__no_emails_received.name
  namespace                 = "mettel_automation/alarms"
  period                    = "600"
  statistic                 = "Sum"
  threshold                 = "10"
  alarm_description         = "Triggers an alarm if no emails get into the inbox in the last 10 minutes"
  insufficient_data_actions = []
alarm_actions = []
}

resource "aws_sns_topic" "intermapper-outage-no-emails-received-in-the-last-10-minutes" {
  name = "intermapper-outage-no-emails-received-in-the-last-10-minutes"
}

resource "aws_sns_topic_subscription" "intermapper-outage-no-emails-received-in-the-last-10-minutes"{
  for_each  = toset(["managedservices@mettel.net", "ndimuro@mettel.net","bsullivan@mettel.net", "mettel.team@intelygenz.com"])
  topic_arn = aws_sns_topic.intermapper-outage-no-emails-received-in-the-last-10-minutes.arn
  protocol = "email"
  endpoint = each.value
}
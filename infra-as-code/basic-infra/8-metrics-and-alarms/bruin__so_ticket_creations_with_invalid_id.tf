resource "aws_cloudwatch_log_metric_filter" "bruin__so_ticket_creations_with_invalid_id" {
  name           = "bruin__so_ticket_creations_with_invalid_id"
  pattern        = "{ $.environment = \"production\" && $.hostname = \"bruin-bridge-*\" && $.message = \"Bruin reported a ticket ID = 0 after SO ticket creation\" }"
  log_group_name = aws_cloudwatch_log_group.eks_log_group.name

  metric_transformation {
    name      = "bruin__so_ticket_creations_with_invalid_id"
    namespace = "mettel_automation/alarms"
    value     = "$.message"
  }
}

resource "aws_cloudwatch_metric_alarm" "intermapper-outage-too-many-down-events-in-the-last-10-minutes" {
  alarm_name                = "bruin-too-many-invalid-service-outage-ticket-creations"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = "1"
  metric_name               = aws_cloudwatch_log_metric_filter.bruin__so_ticket_creations_with_invalid_id.name
  namespace                 = "mettel_automation/alarms"
  period                    = "600"
  statistic                 = "Sum"
  threshold                 = "10"
  alarm_description         = "Triggers an alarm if a fixed number of invalid ticket creations in the last 10 minutes is exceeded"
  insufficient_data_actions = []
alarm_actions = []
}

resource "aws_sns_topic" "intermapper-outage-too-many-down-events-in-the-last-10-minutes" {
  name = "intermapper-outage-too-many-down-events-in-the-last-10-minutes"
}

resource "aws_sns_topic_subscription" "intermapper-outage-too-many-down-events-in-the-last-10-minutes"{
  for_each  = toset(["jhicks@mettel.net", "kiyer@mettel.net", "mettel.team@intelygenz.com"])
  topic_arn = aws_sns_topic.intermapper-outage-too-many-down-events-in-the-last-10-minutes.arn
  protocol = "email"
  endpoint = each.value
}
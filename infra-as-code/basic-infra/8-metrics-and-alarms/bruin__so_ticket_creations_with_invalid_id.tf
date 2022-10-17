resource "aws_cloudwatch_log_metric_filter" "bruin__so_ticket_creations_with_invalid_id" {
  name           = "bruin__so_ticket_creations_with_invalid_id"
  pattern        = "{ $.environment = \"production\" && $.hostname = \"bruin-bridge-*\" && $.message = \"Bruin reported a ticket ID = 0 after SO ticket creation\" }"
  log_group_name = data.aws_cloudwatch_log_group.eks_log_group.name

  metric_transformation {
    name      = "bruin__so_ticket_creations_with_invalid_id"
    namespace = "mettel_automation/alarms"
    value     = "1"
  }
}

resource "aws_cloudwatch_metric_alarm" "bruin-too-many-invalid-service-outage-ticket-creations" {
  alarm_name                = "bruin-too-many-invalid-service-outage-ticket-creations"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = "1"
  metric_name               = aws_cloudwatch_log_metric_filter.bruin__so_ticket_creations_with_invalid_id.name
  namespace                 = "mettel_automation/alarms"
  period                    = "600"
  statistic                 = "Sum"
  threshold                 = "10"
  alarm_description         = "Triggers an alarm if a fixed number of invalid ticket creations is exceeded"
  insufficient_data_actions = []
alarm_actions = []
}

resource "aws_sns_topic" "bruin-too-many-invalid-service-outage-ticket-creations" {
  name = "bruin-too-many-invalid-service-outage-ticket-creations"
}

resource "aws_sns_topic_subscription" "bruin-too-many-invalid-service-outage-ticket-creations"{
  for_each  = toset(["jhicks@mettel.net", "kiyer@mettel.net", "mettel.team@intelygenz.com"])
  topic_arn = aws_sns_topic.bruin-too-many-invalid-service-outage-ticket-creations.arn
  protocol = "email"
  endpoint = each.value
}

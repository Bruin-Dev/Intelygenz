resource "aws_cloudwatch_log_metric_filter" "velocloud_outage__tickets_created" {
  name           = "velocloud_outage__tickets_created"
  pattern        = "{ $.environment = \"production\" && $.hostname = \"som-*\" && $.message = \"*Successfully created outage ticket for edge*\" }"
  log_group_name = aws_cloudwatch_log_group.eks_log_group.name

  metric_transformation {
    name      = "velocloud_outage_tickets_created"
    namespace = "mettel_automation/alarms"
    value     = "1"
  }
}

resource "aws_cloudwatch_metric_alarm" "velocloud-affecting-too-many-tickets-in-the-last-hour" {
  alarm_name                = "velocloud-outage-too-many-tickets-in-the-last-hour"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = "1"
  metric_name               = aws_cloudwatch_log_metric_filter.velocloud_outage__tickets_created.name
  namespace                 = "mettel_automation/alarms"
  period                    = "3600"
  statistic                 = "Sum"
  threshold                 = "51"
  alarm_description         = "Triggers an alarm if the average number of Service Outage tickets created in the last hour is exceeded"
  insufficient_data_actions = []
alarm_actions = []
}

resource "aws_cloudwatch_metric_alarm" "velocloud-outage-no-tickets-created-in-the-last-hour" {
  alarm_name                = "velocloud-outage-no-tickets-created-in-the-last-hour"
  comparison_operator       = "LowerThanOrEqualToThreshold"
  evaluation_periods        = "1"
  metric_name               = aws_cloudwatch_log_metric_filter.velocloud_affecting__tickets_created.name
  namespace                 = "mettel_automation/alarms"
  period                    = "3600"
  statistic                 = "Sum"
  threshold                 = "0"
  alarm_description         = "Triggers an alarm if the average number of Service Outage tickets created in the last hour is exceeded"
  insufficient_data_actions = []
alarm_actions = []
}

resource "aws_sns_topic" "velocloud-outage-no-tickets-created-in-the-last-hour" {
  name = "velocloud-outage-no-tickets-created-in-the-last-hour"
}

resource "aws_sns_topic_subscription" "velocloud-outage-no-tickets-created-in-the-last-hour"{
  for_each  = toset(["HNOCleaderteam@mettel.net", "jhicks@mettel.net", "kiyer@mettel.net", "mettel.team@intelygenz.com"])
  topic_arn = aws_sns_topic.velocloud-outage-no-tickets-created-in-the-last-hour.arn
  protocol = "email"
  endpoint = each.value
}

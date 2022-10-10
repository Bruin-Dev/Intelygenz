resource "aws_cloudwatch_log_metric_filter" "velocloud_affecting__tickets_created" {
  name           = "velocloud_affecting__tickets_created"
  pattern        = "{ $.environment = \"production\" && $.hostname = \"sam-*\" && $.message = \"Service Affecting ticket * was successfully created!*\" }"
  log_group_name = aws_cloudwatch_log_group.eks_log_group.name

  metric_transformation {
    name      = "velocloud_affecting__tickets_created"
    namespace = "mettel_automation/alarms"
    value     = "$.message"
  }
}

resource "aws_cloudwatch_metric_alarm" "velocloud-affecting-too-many-tickets-in-the-last-hour" {
  alarm_name                = "velocloud-affecting-too-many-tickets-in-the-last-hour"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = "1"
  metric_name               = aws_cloudwatch_log_metric_filter.velocloud_affecting__tickets_created.name
  namespace                 = "mettel_automation/alarms"
  period                    = "3600"
  statistic                 = "Sum"
  threshold                 = "45"
  alarm_description         = "Alarm description: Triggers an alarm if the average number of Service Affecting tickets created in the last hour is exceeded"
  insufficient_data_actions = []
alarm_actions = []
}

resource "aws_sns_topic" "velocloud-affecting-too-many-tickets-in-the-last-hour" {
  name = "velocloud-affecting-too-many-tickets-in-the-last-hour"
}

resource "aws_sns_topic_subscription" "velocloud-affecting-too-many-tickets-in-the-last-hour"{
  for_each  = toset(["HNOCleaderteam@mettel.net", "jhicks@mettel.net", "kiyer@mettel.net", "mettel.team@intelygenz.com"])
  topic_arn = aws_sns_topic.velocloud-affecting-too-many-tickets-in-the-last-hour.arn
  protocol = "email"
  endpoint = each.value
}

resource "aws_cloudwatch_log_metric_filter" "velocloud_affecting__tickets_created" {
  name           = "velocloud_affecting__tickets_created"
  pattern        = "{ $.environment = \"production\" && $.hostname = \"sam-*\" && $.message = \"Service Affecting ticket * was successfully created!*\" }"
  log_group_name = data.aws_cloudwatch_log_group.eks_log_group.name

  metric_transformation {
    name      = "velocloud_affecting__tickets_created"
    namespace = "mettel_automation/alarms"
    value     = "1"
  }
}

resource "aws_cloudwatch_metric_alarm" "velocloud-affecting-too-many-tickets" {
  alarm_name                = "velocloud-affecting-too-many-tickets"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = "1"
  metric_name               = aws_cloudwatch_log_metric_filter.velocloud_affecting__tickets_created.name
  namespace                 = "mettel_automation/alarms"
  period                    = "3600"
  statistic                 = "Sum"
  threshold                 = "50"
  alarm_description         = "Triggers an alarm if the average number of Service Affecting tickets created is exceeded"
  insufficient_data_actions = []
  actions_enabled           = "true"
  alarm_actions             = [aws_sns_topic.velocloud-affecting-too-many-tickets.arn]
}

resource "aws_sns_topic" "velocloud-affecting-too-many-tickets" {
  name = "velocloud-affecting-too-many-tickets"
}

resource "aws_sns_topic_subscription" "velocloud-affecting-too-many-tickets" {
  for_each  = toset(["HNOCleaderteam@mettel.net", "jhicks@mettel.net", "kiyer@mettel.net", "mettel.team@intelygenz.com"])
  topic_arn = aws_sns_topic.velocloud-affecting-too-many-tickets.arn
  protocol  = "email"
  endpoint  = each.value
}

resource "aws_cloudwatch_metric_alarm" "velocloud-affecting-no-tickets-created" {
  alarm_name                = "velocloud-affecting-no-tickets-created"
  comparison_operator       = "LessThanOrEqualToThreshold"
  evaluation_periods        = "1"
  metric_name               = aws_cloudwatch_log_metric_filter.velocloud_affecting__tickets_created.name
  namespace                 = "mettel_automation/alarms"
  period                    = "3600"
  statistic                 = "Sum"
  threshold                 = "0"
  alarm_description         = "Triggers an alarm if the average number of Service Affecting tickets created is exceeded"
  insufficient_data_actions = []
  actions_enabled           = "true"
  alarm_actions             = [aws_sns_topic.velocloud-affecting-no-tickets-created.arn]
}

resource "aws_sns_topic" "velocloud-affecting-no-tickets-created" {
  name = "velocloud-affecting-no-tickets-created"
}

resource "aws_sns_topic_subscription" "velocloud-affecting-no-tickets-created" {
  for_each  = toset(["mettel.team@intelygenz.com"])
  topic_arn = aws_sns_topic.velocloud-affecting-no-tickets-created.arn
  protocol  = "email"
  endpoint  = each.value
}

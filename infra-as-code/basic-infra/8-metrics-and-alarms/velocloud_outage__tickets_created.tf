resource "aws_cloudwatch_log_metric_filter" "velocloud_outage__tickets_created" {
  name           = "velocloud_outage__tickets_created"
  pattern        = "{ $.environment = \"production\" && $.hostname = \"som-*\" && $.message = \"*Successfully created outage ticket for edge*\" }"
  log_group_name = data.aws_cloudwatch_log_group.eks_log_group.name

  metric_transformation {
    name      = "velocloud_outage__tickets_created"
    namespace = "mettel_automation/alarms"
    value     = "1"
  }
}

resource "aws_cloudwatch_metric_alarm" "velocloud-outage-too-many-tickets" {
  alarm_name                = "velocloud-outage-too-many-tickets"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = "1"
  metric_name               = aws_cloudwatch_log_metric_filter.velocloud_outage__tickets_created.name
  namespace                 = "mettel_automation/alarms"
  period                    = "3600"
  statistic                 = "Sum"
  threshold                 = "50"
  alarm_description         = "Triggers an alarm if the average number of Service Outage tickets created is exceeded"
  insufficient_data_actions = []
  actions_enabled           = "true"
  alarm_actions             = [aws_sns_topic.velocloud-outage-too-many-tickets.arn]
}

resource "aws_sns_topic" "velocloud-outage-too-many-tickets" {
  name = "velocloud-outage-too-many-tickets"
}

resource "aws_sns_topic_subscription" "velocloud-outage-too-many-tickets"{
  for_each  = toset(["HNOCleaderteam@mettel.net", "jhicks@mettel.net", "kiyer@mettel.net", "mettel.team@intelygenz.com"])
  topic_arn = aws_sns_topic.velocloud-outage-too-many-tickets.arn
  protocol = "email"
  endpoint = each.value
}

resource "aws_cloudwatch_metric_alarm" "velocloud-outage-no-tickets-created" {
  alarm_name                = "velocloud-outage-no-tickets-created"
  comparison_operator       = "LessThanOrEqualToThreshold"
  evaluation_periods        = "1"
  metric_name               = aws_cloudwatch_log_metric_filter.velocloud_outage__tickets_created.name
  namespace                 = "mettel_automation/alarms"
  period                    = "3600"
  statistic                 = "Sum"
  threshold                 = "0"
  alarm_description         = "Triggers an alarm if the average number of Service Outage tickets created is exceeded"
  insufficient_data_actions = []
  actions_enabled           = "true"
  alarm_actions             = [aws_sns_topic.velocloud-outage-no-tickets-created.arn]
}

resource "aws_sns_topic" "velocloud-outage-no-tickets-created" {
  name = "velocloud-outage-no-tickets-created"
}


resource "aws_sns_topic_subscription" "velocloud-outage-no-tickets-created"{
  for_each  = toset(["mettel.team@intelygenz.com"])
  topic_arn = aws_sns_topic.velocloud-outage-no-tickets-created.arn
  protocol = "email"
  endpoint = each.value
}

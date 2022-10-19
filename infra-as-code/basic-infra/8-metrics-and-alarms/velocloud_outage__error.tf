resource "aws_cloudwatch_log_metric_filter" "velocloud_outage__error" {
  name           = "velocloud_outage__error"
  pattern        = "{ $.environment = \"production\" && $.hostname = \"som-*\" && $.log_level = \"ERROR\" }"
  log_group_name = data.aws_cloudwatch_log_group.eks_log_group.name

  metric_transformation {
    name      = "velocloud_outage__error"
    namespace = "mettel_automation/alarms"
    value     = "1"
  }
}

resource "aws_cloudwatch_metric_alarm" "velocloud-outage-too-many-errors" {
  alarm_name                = "velocloud-outage-too-many-errors"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = "1"
  metric_name               = aws_cloudwatch_log_metric_filter.velocloud_outage__error.name
  namespace                 = "mettel_automation/alarms"
  period                    = "3600"
  statistic                 = "Sum"
  threshold                 = "500"
  alarm_description         = "Triggers an alarm if the Velocloud Outage reported too many errors"
  insufficient_data_actions = []
  actions_enabled           = "true"
  alarm_actions             = [aws_sns_topic.velocloud-outage-too-many-errors.arn]
}

resource "aws_sns_topic" "velocloud-outage-too-many-errors" {
  name = "velocloud-outage-too-many-errors"
}

resource "aws_sns_topic_subscription" "velocloud-outage-too-many-errors"{
  for_each  = toset(["mettel.team@intelygenz.com"])
  topic_arn = aws_sns_topic.velocloud-outage-too-many-errors.arn
  protocol  = "email"
  endpoint  = each.value
}

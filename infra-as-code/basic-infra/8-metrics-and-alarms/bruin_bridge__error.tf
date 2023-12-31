resource "aws_cloudwatch_log_metric_filter" "bruin_bridge__error" {
  name           = "bruin_bridge__error"
  pattern        = "{ $.environment = \"production\" && $.hostname = \"bruin-bridge-*\" && $.log_level = \"ERROR\" }"
  log_group_name = data.aws_cloudwatch_log_group.eks_log_group.name

  metric_transformation {
    name      = "bruin_bridge__error"
    namespace = "mettel_automation/alarms"
    value     = "1"
  }
}

resource "aws_cloudwatch_metric_alarm" "bruin-bridge-too-many-errors" {
  alarm_name                = "bruin-bridge-too-many-errors"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = "1"
  metric_name               = aws_cloudwatch_log_metric_filter.bruin_bridge__error.name
  namespace                 = "mettel_automation/alarms"
  period                    = "3600"
  statistic                 = "Sum"
  threshold                 = "1000"
  alarm_description         = "Triggers an alarm if the Bruin Bridge reported too many errors"
  insufficient_data_actions = []
  actions_enabled           = "true"
  alarm_actions             = [aws_sns_topic.bruin-bridge-too-many-errors.arn]
}

resource "aws_sns_topic" "bruin-bridge-too-many-errors" {
  name = "bruin-bridge-too-many-errors"
}

resource "aws_sns_topic_subscription" "bruin-bridge-too-many-errors" {
  for_each  = toset(["mettel.team@intelygenz.com"])
  topic_arn = aws_sns_topic.bruin-bridge-too-many-errors.arn
  protocol  = "email"
  endpoint  = each.value
}

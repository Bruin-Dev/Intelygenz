resource "aws_cloudwatch_log_metric_filter" "email__login_errors" {
  name           = "email__login_errors"
  pattern        = "{ $.environment = \"production\" && $.hostname = \"email-bridge-*\" && $.message = \"There was an error trying to login into the inbox*\" }"
  log_group_name = data.aws_cloudwatch_log_group.eks_log_group.name

  metric_transformation {
    name      = "email__login_errors"
    namespace = "mettel_automation/alarms"
    value     = "1"
  }
}

resource "aws_cloudwatch_metric_alarm" "emails-error-logging-in-to-the-inbox" {
  alarm_name                = "emails-error-logging-in-to-the-inbox"
  comparison_operator       = "LessThanOrEqualToThreshold"
  evaluation_periods        = "1"
  metric_name               = aws_cloudwatch_log_metric_filter.email__login_errors.name
  namespace                 = "mettel_automation/alarms"
  period                    = "3600"
  statistic                 = "Sum"
  threshold                 = "0"
  alarm_description         = "Triggers an alarm if there is an error while logging in to the email inbox"
  insufficient_data_actions = []
  actions_enabled           = "true"
  alarm_actions             = [aws_sns_topic.emails-error-logging-in-to-the-inbox.arn]
}

resource "aws_sns_topic" "emails-error-logging-in-to-the-inbox" {
  name = "emails-error-logging-in-to-the-inbox"
}

resource "aws_sns_topic_subscription" "emails-error-logging-in-to-the-inbox"{
  for_each  = toset(["mettel.team@intelygenz.com"])
  topic_arn = aws_sns_topic.emails-error-logging-in-to-the-inbox.arn
  protocol = "email"
  endpoint = each.value
}
resource "aws_cloudwatch_log_metric_filter" "velocloud_outage__triage_job_finished" {
  name           = "velocloud_outage__triage_job_finished"
  pattern        = "{ $.environment = \"production\" && $.hostname = \"som-*\" && $.message = \"Triage process finished!\" }"
  log_group_name = aws_cloudwatch_log_group.eks_log_group.name

  metric_transformation {
    name      = "velocloud_outage__triage_job_finished"
    namespace = "mettel_automation/alarms"
    value     = "1"
  }
}

resource "aws_cloudwatch_metric_alarm" "velocloud-outage-triage-job-failed" {
  alarm_name                = "velocloud-outage-triage-job-failed"
  comparison_operator       = "LowerThanOrEqualToThreshold"
  evaluation_periods        = "1"
  metric_name               = aws_cloudwatch_log_metric_filter.velocloud_outage__triage_job_finished.name
  namespace                 = "mettel_automation/alarms"
  period                    = "3600"
  statistic                 = "Sum"
  threshold                 = "0"
  alarm_description         = "Triggers an alarm if no Triage job finished successfully in the last hour"
  insufficient_data_actions = []
alarm_actions = []
}

resource "aws_sns_topic" "velocloud-outage-triage-job-failed" {
  name = "velocloud-outage-triage-job-failed"
}

resource "aws_sns_topic_subscription" "velocloud-outage-triage-job-failed"{
  for_each  = toset(["mettel.team@intelygenz.com"])
  topic_arn = aws_sns_topic.velocloud-outage-triage-job-failed.arn
  protocol = "email"
  endpoint = each.value
}
resource "aws_cloudwatch_metric_alarm" "cluster_task_running" {
  alarm_name                = local.cluster_task_running-alarm_name
  comparison_operator       = "LessThanThreshold"
  evaluation_periods        = "2"
  metric_name               = "CPUUtilization"
  namespace                 = "AWS/EC2"
  period                    = "120"
  statistic                 = "Average"
  threshold                 = "80"
  alarm_description         = "This metric monitors tasks for each service with running state"
  insufficient_data_actions = []
}
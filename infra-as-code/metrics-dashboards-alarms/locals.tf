locals {
  // metrics local variables
  exception_detected_metric-metric_transformation-name = "ExceptionMessagesDetectedInServices"

  // dashboards local variables
  cluster_dashboard_name = "cluster-${var.ENVIRONMENT}"

  // alarms local variables
  cluster_task_running-alarm_name = "tasks_running-${var.ENVIRONMENT}"

  // cloudfourmation local variables
  stack_alarms-name = "SnsTopicAlarmErrorMessagesStack"
}
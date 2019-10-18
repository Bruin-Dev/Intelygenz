locals {
  // dashboards local variables
  cluster_dashboard_name = "cluster-${var.ENVIRONMENT}"

  // alarms local variables
  cluster_task_running-alarm_name = "tasks_running-${var.ENVIRONMENT}"
}
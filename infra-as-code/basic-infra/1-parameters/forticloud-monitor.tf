resource "aws_ssm_parameter" "parameter-forticloud-monitor-task-auto-resolution-grace-seconds" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/forticloud-monitor/task-auto-resolution-grace-seconds"
  description = "Grace period in seconds for the monitor to auto-resolve bruin tasks"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "TASK_AUTO_RESOLUTION_GRACE_SECONDS"
    note = "can be updated from the parameter store dashboard"
  })
}
resource "aws_ssm_parameter" "parameter-forticloud-monitor-task-max-auto-resolutions" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/forticloud-monitor/task-max-auto-resolutions"
  description = "Managements statuses to store devices in cache "
  type        = "SecureString"
  value       = "-"
  # to edit go to parameter store dashboard.
  key_id = aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "TASK_MAX_AUTO_RESOLUTIONS"
    note = "can be updated from the parameter store dashboard"
  })
}

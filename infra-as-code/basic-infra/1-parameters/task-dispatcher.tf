resource "aws_ssm_parameter" "parameter-task-dispatcher-dispatching-job-interval" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/task-dispatcher/dispatching-job-interval"
  description = "Defines how often due tasks are dispatched"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "DISPATCHING_JOB_INTERVAL"
    note = "can be updated from the parameter store dashboard"
  })
}

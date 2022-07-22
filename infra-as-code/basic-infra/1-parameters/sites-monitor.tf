resource "aws_ssm_parameter" "parameter-sites-monitor-monitored-velocloud-hosts" {
  name        = "/automation-engine/${local.env}/sites-monitor/monitored-velocloud-hosts"
  description = "VeloCloud hosts whose edges will be monitored"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MONITORED_VELOCLOUD_HOSTS"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-sites-monitor-monitoring-job-interval" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/sites-monitor/monitoring-job-interval"
  description = "Defines how often to look for links and edges, and write their data to the metrics server"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MONITORING_JOB_INTERVAL"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-last-contact-report-monitored-velocloud-hosts" {
  name        = "/automation-engine/${local.env}/last-contact-report/monitored-velocloud-hosts"
  description = "VeloCloud hosts whose edges will be used to build the report"
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

resource "aws_ssm_parameter" "parameter-last-contact-report-report-recipient" {
  name        = "/automation-engine/${local.env}/last-contact-report/report-recipient"
  description = "Email address to send the report to"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "RECIPIENT"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-velocloud-bridge-velocloud-credentials" {
  name        = "/automation-engine/${local.env}/velocloud-bridge/velocloud-credentials"
  description = "Velocloud credentials"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "VELOCLOUD_CREDENTIALS"
    note = "can be updated from the parameter store dashboard"
  })
}

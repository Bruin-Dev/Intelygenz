/*resource "aws_ssm_parameter" "parameter-forticloud-bridge-forticloud-credentials" {
  name        = "/automation-engine/${local.env}/forticloud-bridge/forticloud-credentials"
  description = "Forticloud credentials"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "FORTICLOUD_CREDENTIALS"
    note = "can be updated from the parameter store dashboard"
  })
}
*/
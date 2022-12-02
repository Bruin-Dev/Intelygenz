resource "aws_ssm_parameter" "parameter-repair-tickets-kre-bridge-kre-base-url" {
  name        = "/automation-engine/${local.env}/repair-tickets-kre-bridge/kre-base-url"
  description = "Base URL for Repair tickets' KRE"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "KRE_BASE_URL"
    note = "can be updated from the parameter store dashboard"
  })
}

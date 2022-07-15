resource "aws_ssm_parameter" "parameter-notifications-bridge-slack-webhook-url" {
  name        = "/automation-engine/${local.env}/notifications-bridge/slack-webhook-url"
  description = "Slack webhook to send messages"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "SLACK_WEBHOOK"
    note = "can be updated from the parameter store dashboard"
  })
}

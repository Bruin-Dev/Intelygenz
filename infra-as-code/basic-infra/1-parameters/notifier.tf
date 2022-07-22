resource "aws_ssm_parameter" "parameter-notifier-email-account-for-message-delivery-password" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/notifier/email-account-for-message-delivery-password"
  description = "Email account used to send messages to other accounts (password)"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "EMAIL_ACCOUNT_FOR_MESSAGE_DELIVERY_PASSWORD"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-notifier-email-account-for-message-delivery-username" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/notifier/email-account-for-message-delivery-username"
  description = "Email account used to send messages to other accounts (username)"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "EMAIL_ACCOUNT_FOR_MESSAGE_DELIVERY_USERNAME"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-notifier-monitorable-email-accounts" {
  name        = "/automation-engine/${local.env}/notifier/monitorable-email-accounts"
  description = "Mapping of e-mail addresses and passwords whose inboxes can be read for later analysis"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MONITORABLE_EMAIL_ACCOUNTS"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-notifier-slack-webhook-url" {
  name        = "/automation-engine/${local.env}/notifier/slack-webhook-url"
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

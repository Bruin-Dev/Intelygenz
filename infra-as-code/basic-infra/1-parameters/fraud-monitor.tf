resource "aws_ssm_parameter" "parameter-fraud-monitor-default-client-info-for-did-without-inventory" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/fraud-monitor/default-client-info-for-did-without-inventory"
  description = "Default client info used when the DID device in the Fraud alert does not have an inventory assigned in Bruin"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "DEFAULT_CLIENT_INFO_FOR_DID_WITHOUT_INVENTORY"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-fraud-monitor-default-contact-for-new-tickets" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/fraud-monitor/default-contact-for-new-tickets"
  description = "Default contact details used when a Fraud is reported as a Service Affecting ticket"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "DEFAULT_CONTACT_FOR_NEW_TICKETS"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-fraud-monitor-monitoring-job-interval" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/fraud-monitor/monitoring-job-interval"
  description = "Defines how often Fraud e-mails are checked to report them as Service Affecting tickets"
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

resource "aws_ssm_parameter" "parameter-fraud-monitor-observed-inbox-email-address" {
  name        = "/automation-engine/${local.env}/fraud-monitor/observed-inbox-email-address"
  description = "E-mail account that receives Fraud e-mails for later analysis"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "OBSERVED_INBOX_EMAIL_ADDRESS"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-fraud-monitor-observed-inbox-senders" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/fraud-monitor/observed-inbox-senders"
  description = "Senders addresses whose e-mail messages represent Fraud alerts"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "OBSERVED_INBOX_SENDERS"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-fraud-monitor-alerts-lookup-days" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/fraud-monitor/alerts-lookup-days"
  description = "How many days to look back for Fraud alerts in the desired e-mail inbox"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "ALERTS_LOOKUP_DAYS"
    note = "can be updated from the parameter store dashboard"
  })
}

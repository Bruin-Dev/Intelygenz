resource "aws_ssm_parameter" "parameter-email-tagger-monitor-api-endpoint-prefix" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/email-tagger-monitor/api-endpoint-prefix"
  description = "API server endpoint prefix for incoming requests"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "API_ENDPOINT_PREFIX"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-email-tagger-monitor-api-request-key" {
  name        = "/automation-engine/${local.env}/email-tagger-monitor/api-request-key"
  description = "API request key for incoming requests"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "API_REQUEST_KEY"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-email-tagger-monitor-api-request-signature-secret-key" {
  name        = "/automation-engine/${local.env}/email-tagger-monitor/api-request-signature-secret-key"
  description = "API signature secret key for incoming requests"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "API_REQUEST_SIGNATURE_SECRET_KEY"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-email-tagger-monitor-max-concurrent-emails" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/email-tagger-monitor/max-concurrent-emails"
  description = "Defines how many simultaneous emails are processed"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MAX_CONCURRENT_EMAILS"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-email-tagger-monitor-max-concurrent-tickets" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/email-tagger-monitor/max-concurrent-tickets"
  description = "Defines how many simultaneous tickets are sent to the KRE to train the AI model"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MAX_CONCURRENT_TICKETS"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-email-tagger-monitor-new-emails-job-interval" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/email-tagger-monitor/new-emails-job-interval"
  description = "Defines how often new emails received from Bruin are processed"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "NEW_EMAILS_JOB_INTERVAL"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-email-tagger-monitor-new-tickets-job-interval" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/email-tagger-monitor/new-tickets-job-interval"
  description = "Defines how often new tickets received from Bruin are sent to the KRE to train the AI model"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "NEW_TICKETS_JOB_INTERVAL"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-email-tagger-monitor-store-replies-enabled" {
  name        = "/automation-engine/${local.env}/email-tagger-monitor/store-replies-enabled"
  description = "If enabled, stores any valid reply for RTA to process it"
  type        = "String"
  value       = "false"  # to edit go to parameter store dashboard.

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "STORE_REPLIES_ENABLED"
    note = "can be updated from the parameter store dashboard"
  })
}

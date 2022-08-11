resource "aws_ssm_parameter" "parameter-repair-tickets-monitor-max-concurrent-closed-tickets-for-feedback" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/repair-tickets-monitor/max-concurrent-closed-tickets-for-feedback"
  description = "Defines how many simultaneous new closed tickets are sent to the KRE to train the AI model"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MAX_CONCURRENT_CLOSED_TICKETS_FOR_FEEDBACK"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-repair-tickets-monitor-max-concurrent-created-tickets-for-feedback" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/repair-tickets-monitor/max-concurrent-created-tickets-for-feedback"
  description = "Defines how many simultaneous new created tickets are sent to the KRE to train the AI model"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MAX_CONCURRENT_CREATED_TICKETS_FOR_FEEDBACK"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-repair-tickets-monitor-max-concurrent-emails-for-monitoring" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/repair-tickets-monitor/max-concurrent-emails-for-monitoring"
  description = "Defines how many simultaneous tagged emails are processed"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MAX_CONCURRENT_EMAILS_FOR_MONITORING"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-repair-tickets-monitor-max-concurrent-old-parent-emails-reprocessing" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/repair-tickets-monitor/max-concurrent-old-parent-emails-reprocessing"
  description = "Defines how many simultaneous old parent emails are reprocessed"
  type        = "String"
  value       = "0"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MAX_CONCURRENT_OLD_PARENT_EMAILS_REPROCESSING"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-repair-tickets-monitor-new-closed-tickets-feedback-job-interval" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/repair-tickets-monitor/new-closed-tickets-feedback-job-interval"
  description = "Defines how often new closed tickets fetched from Bruin are sent to the KRE to train the AI model"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "NEW_CLOSED_TICKETS_FEEDBACK_JOB_INTERVAL"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-repair-tickets-monitor-new-created-tickets-feedback-job-interval" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/repair-tickets-monitor/new-created-tickets-feedback-job-interval"
  description = "Defines how often new created tickets fetched from Bruin are sent to the KRE to train the AI model"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "NEW_CREATED_TICKETS_FEEDBACK_JOB_INTERVAL"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-repair-tickets-monitor-rta-monitor-job-interval" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/repair-tickets-monitor/rta-monitor-job-interval"
  description = "Defines how often new emails tagged by the E-mail Tagger are processed"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "RTA_MONITOR_JOB_INTERVAL"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-repair-tickets-monitor-old-parent-emails-reprocessing-job-interval" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/repair-tickets-monitor/old-parent-emails-reprocessing-job-interval"
  description = "Defines how often old parent emails are reprocessed"
  type        = "String"
  value       = "0"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "OLD_PARENT_EMAILS_REPROCESSING_JOB_INTERVAL"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-repair-tickets-monitor-tag-ids-mapping" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/repair-tickets-monitor/tag-ids-mapping"
  description = "Mapping of tag names and their corresponding numeric ID, as defined in the AI model"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "TAG_IDS_MAPPING"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-repair-tickets-monitor-auto-reply-enabled" {
  name        = "/automation-engine/${local.env}/repair-tickets-monitor/auto-reply-enabled"
  description = "Boolean flag to enable the auto-reply feature"
  type        = "String"
  value       = "false"  # to edit go to parameter store dashboard.

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "AUTO_REPLY_ENABLED"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-repair-tickets-monitor-auto-reply-whitelist" {
  name        = "/automation-engine/${local.env}/repair-tickets-monitor/auto-reply-whitelist"
  description = "Whitelist of email addresses to which auto-reply. An empty list means all addresses can be auto-replied"
  type        = "SecureString"
  value       = "[]"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "AUTO_REPLY_WHITELIST"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-repair-tickets-monitor-old-parent-email-ttl-seconds" {
  name        = "/automation-engine/${local.env}/repair-tickets-monitor/old-parent-email-ttl-seconds"
  description = "Time to wait for a client reply before sending the parent email back to the `New` queue"
  type        = "String"
  value       = "0"  # to edit go to parameter store dashboard.

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "OLD_PARENT_EMAIL_TTL_SECONDS"
    note = "can be updated from the parameter store dashboard"
  })
}

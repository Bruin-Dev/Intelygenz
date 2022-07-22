resource "aws_ssm_parameter" "parameter-intermapper-outage-monitor-dri-parameters-for-piab-notes" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/intermapper-outage-monitor/dri-parameters-for-piab-notes"
  description = "Parameters to fetch from DRI to include them in InterMapper notes for PIAB devices"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "DRI_PARAMETERS_FOR_PIAB_NOTES"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-intermapper-outage-monitor-grace-period-to-autoresolve-after-last-documented-outage-day-time" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/intermapper-outage-monitor/grace-period-to-autoresolve-after-last-documented-outage-day-time"
  description = "Defines for how long a ticket can be auto-resolved after the last documented outage"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_OUTAGE_DAY_TIME"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-intermapper-outage-monitor-grace-period-to-autoresolve-after-last-documented-outage-night-time" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/intermapper-outage-monitor/grace-period-to-autoresolve-after-last-documented-outage-night-time"
  description = "Defines for how long a ticket can be auto-resolved after the last documented outage"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_OUTAGE_NIGHT_TIME"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-intermapper-outage-monitor-max-autoresolves-per-ticket" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/intermapper-outage-monitor/max-autoresolves-per-ticket"
  description = "Defines how many times a ticket can be auto-resolved"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MAX_AUTORESOLVES_PER_TICKET"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-intermapper-outage-monitor-max-concurrent-email-batches" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/intermapper-outage-monitor/max-concurrent-email-batches"
  description = "Defines how many simultaneous email batches related to the same InterMapper asset are processed"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MAX_CONCURRENT_EMAIL_BATCHES"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-intermapper-outage-monitor-monitored-down-events" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/intermapper-outage-monitor/monitored-down-events"
  description = "InterMapper events considered as DOWN"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MONITORED_DOWN_EVENTS"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-intermapper-outage-monitor-monitored-up-events" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/intermapper-outage-monitor/monitored-up-events"
  description = "InterMapper events considered as UP"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MONITORED_UP_EVENTS"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-intermapper-outage-monitor-monitoring-job-interval" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/intermapper-outage-monitor/monitoring-job-interval"
  description = "Defines how often InterMapper events are checked to find and report issues"
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

resource "aws_ssm_parameter" "parameter-intermapper-outage-monitor-observed-inbox-email-address" {
  name        = "/automation-engine/${local.env}/intermapper-outage-monitor/observed-inbox-email-address"
  description = "E-mail account that receives InterMapper events for later analysis"
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

resource "aws_ssm_parameter" "parameter-intermapper-outage-monitor-observed-inbox-senders" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/intermapper-outage-monitor/observed-inbox-senders"
  description = "Senders addresses whose e-mail messages represent InterMapper events"
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

resource "aws_ssm_parameter" "parameter-intermapper-outage-monitor-whitelisted-product-categories-for-autoresolve" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/intermapper-outage-monitor/whitelisted-product-categories-for-autoresolve"
  description = "Defines which Bruin product categories are taken into account when auto-resolving tickets"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "WHITELISTED_PRODUCT_CATEGORIES_FOR_AUTORESOLVE"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-intermapper-outage-monitor-events-lookup-days" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/intermapper-outage-monitor/events-lookup-days"
  description = "How many days to look back for InterMapper events in the desired e-mail inbox"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "EVENTS_LOOKUP_DAYS"
    note = "can be updated from the parameter store dashboard"
  })
}

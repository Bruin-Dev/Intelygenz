resource "aws_ssm_parameter" "parameter-tnba-monitor-blacklisted-edges" {
  name        = "/automation-engine/${local.env}/tnba-monitor/blacklisted-edges"
  description = "List of edges that are excluded from TNBA monitoring"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "BLACKLISTED_EDGES"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-tnba-monitor-grace-period-before-appending-new-tnba-notes" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/tnba-monitor/grace-period-before-appending-new-tnba-notes"
  description = "Defines for how long a ticket needs to wait since it was opened before appending a new TNBA note"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "GRACE_PERIOD_BEFORE_APPENDING_NEW_TNBA_NOTES"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-tnba-monitor-grace-period-before-monitoring-tickets-based-on-last-documented-outage" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/tnba-monitor/grace-period-before-monitoring-tickets-based-on-last-documented-outage"
  description = "Defines for how long a Service Outage ticket needs to wait after the last documented outage to get a new TNBA note appended"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "GRACE_PERIOD_BEFORE_MONITORING_TICKETS_BASED_ON_LAST_DOCUMENTED_OUTAGE"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-tnba-monitor-min-required-confidence-for-request-and-repair-completed-predictions" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/tnba-monitor/min-required-confidence-for-request-and-repair-completed-predictions"
  description = "Defines the minimum confidence level required to consider a Request Completed / Repair Completed prediction accurate in TNBA auto-resolves"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MIN_REQUIRED_CONFIDENCE_FOR_REQUEST_AND_REPAIR_COMPLETED_PREDICTIONS"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-tnba-monitor-monitored-product-category" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/tnba-monitor/monitored-product-category"
  description = "Bruin's product category under monitoring"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MONITORED_PRODUCT_CATEGORY"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-tnba-monitor-monitored-velocloud-hosts" {
  name        = "/automation-engine/${local.env}/tnba-monitor/monitored-velocloud-hosts"
  description = "VeloCloud hosts whose edges will be monitored"
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

resource "aws_ssm_parameter" "parameter-tnba-monitor-monitoring-job-interval" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/tnba-monitor/monitoring-job-interval"
  description = "Defines how often tickets are checked to see if they need a new TNBA note"
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

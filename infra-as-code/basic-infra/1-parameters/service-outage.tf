resource "aws_ssm_parameter" "parameter-service-outage-monitor-blacklisted-edges" {
  name        = "/automation-engine/${local.env}/service-outage/monitor/blacklisted-edges"
  description = "List of edges that are excluded from Service Outage monitoring"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MONITORING__BLACKLISTED_EDGES"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-outage-monitor-grace-period-to-autoresolve-after-last-documented-outage-day-time" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-outage/monitor/grace-period-to-autoresolve-after-last-documented-outage-day-time"
  description = "Defines for how long the monitor will wait before attempting a new DiGi Reboot on an edge"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MONITORING__GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_OUTAGE_DAY_TIME"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-outage-monitor-grace-period-to-autoresolve-after-last-documented-outage-night-time" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-outage/monitor/grace-period-to-autoresolve-after-last-documented-outage-night-time"
  description = "Defines for how long the monitor will wait before attempting a new DiGi Reboot on an edge"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MONITORING__GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_OUTAGE_NIGHT_TIME"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-outage-monitor-grace-period-before-attempting-new-digi-reboots" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-outage/monitor/grace-period-before-attempting-new-digi-reboots"
  description = "Defines for how long the monitor will wait before attempting a new DiGi Reboot on an edge"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MONITORING__GRACE_PERIOD_BEFORE_ATTEMPTING_NEW_DIGI_REBOOTS"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-outage-monitor-link-labels-blacklisted-in-asr-forwards" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-outage/monitor/link-labels-blacklisted-in-asr-forwards"
  description = "List of link labels that are excluded from forwards to the ASR queue"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MONITORING__LINK_LABELS_BLACKLISTED_IN_ASR_FORWARDS"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-outage-monitor-link-labels-blacklisted-in-hnoc-forwards" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-outage/monitor/link-labels-blacklisted-in-hnoc-forwards"
  description = "List of link labels that are excluded from forwards to the HNOC queue"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MONITORING__LINK_LABELS_BLACKLISTED_IN_HNOC_FORWARDS"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-outage-monitor-max-autoresolves-per-ticket" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-outage/monitor/max-autoresolves-per-ticket"
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
    Name = "MONITORING__MAX_AUTORESOLVES_PER_TICKET"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-outage-monitor-missing-edges-from-cache-report-recipient" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-outage/monitor/missing-edges-from-cache-report-recipient"
  description = "E-mail address that will receive a tiny report showing which edges from VeloCloud responses are not in the cache of customers"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MONITORING__MISSING_EDGES_FROM_CACHE_REPORT_RECIPIENT"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-outage-monitor-monitored-velocloud-hosts" {
  name        = "/automation-engine/${local.env}/service-outage/monitor/monitored-velocloud-hosts"
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

resource "aws_ssm_parameter" "parameter-service-outage-monitor-monitoring-job-interval" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-outage/monitor/monitoring-job-interval"
  description = "Defines how often devices are checked to find and report issues"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MONITORING__MONITORING_JOB_INTERVAL"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-outage-monitor-quarantine-for-edges-in-ha-hard-down-outage" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-outage/monitor/quarantine-for-edges-in-ha-hard-down-outage"
  description = "Defines how much time to wait before re-checking an edge currently in Hard Down (HA) state"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MONITORING__QUARANTINE_FOR_EDGES_IN_HA_HARD_DOWN_OUTAGE"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-outage-monitor-quarantine-for-edges-in-ha-link-down-outage" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-outage/monitor/quarantine-for-edges-in-ha-link-down-outage"
  description = "Defines how much time to wait before re-checking an edge currently in Link Down (HA) state"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MONITORING__QUARANTINE_FOR_EDGES_IN_HA_LINK_DOWN_OUTAGE"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-outage-monitor-quarantine-for-edges-in-ha-soft-down-outage" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-outage/monitor/quarantine-for-edges-in-ha-soft-down-outage"
  description = "Defines how much time to wait before re-checking an edge currently in Soft Down (HA) state"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MONITORING__QUARANTINE_FOR_EDGES_IN_HA_SOFT_DOWN_OUTAGE"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-outage-monitor-quarantine-for-edges-in-hard-down-outage" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-outage/monitor/quarantine-for-edges-in-hard-down-outage"
  description = "Defines how much time to wait before re-checking an edge currently in Hard Down state"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MONITORING__QUARANTINE_FOR_EDGES_IN_HARD_DOWN_OUTAGE"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-outage-monitor-quarantine-for-edges-in-link-down-outage" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-outage/monitor/quarantine-for-edges-in-link-down-outage"
  description = "Defines how much time to wait before re-checking an edge currently in Link Down state"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MONITORING__QUARANTINE_FOR_EDGES_IN_LINK_DOWN_OUTAGE"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-outage-monitor-severity-for-edge-down-outages" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-outage/monitor/severity-for-edge-down-outages"
  description = "Severity level for Edge Down outages"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MONITORING__SEVERITY_FOR_EDGE_DOWN_OUTAGES"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-outage-monitor-severity-for-link-down-outages" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-outage/monitor/severity-for-link-down-outages"
  description = "Severity level for Link Down outages"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MONITORING__SEVERITY_FOR_LINK_DOWN_OUTAGES"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-outage-monitor-wait-time-before-sending-new-milestone-reminder" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-outage/monitor/wait-time-before-sending-new-milestone-reminder"
  description = "How long we need to wait for the milestone reminder email to be sent"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MONITORING__WAIT_TIME_BEFORE_SENDING_NEW_MILESTONE_REMINDER"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-outage-monitor-business-grade-link-labels" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-outage/monitor/business-grade-link-labels"
  description = "List of labels that define a link as business grade"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MONITORING__BUSINESS_GRADE_LINK_LABELS"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-outage-monitored-product-category" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-outage/monitored-product-category"
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

resource "aws_ssm_parameter" "parameter-service-outage-triage-max-events-per-event-note" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-outage/triage/max-events-per-event-note"
  description = "Defines how many events will be included in events notes"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "TRIAGE__MAX_EVENTS_PER_EVENT_NOTE"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-outage-triage-monitored-velocloud-hosts" {
  name        = "/automation-engine/${local.env}/service-outage/triage/monitored-velocloud-hosts"
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
    Name = "TRIAGE__MONITORED_VELOCLOUD_HOSTS"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-outage-triage-monitoring-job-interval" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-outage/triage/monitoring-job-interval"
  description = "Defines how often tickets are checked to see if it needs an initial triage or events note"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "TRIAGE__MONITORING_JOB_INTERVAL"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-outage-triage-last-note-interval" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-outage/triage/last-note-interval"
  description = "Defines how long the last note on a ticket is considered recent"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "TRIAGE__LAST_NOTE_INTERVAL"
    note = "can be updated from the parameter store dashboard"
  })
}

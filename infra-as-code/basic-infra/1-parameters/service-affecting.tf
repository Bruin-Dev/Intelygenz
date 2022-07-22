resource "aws_ssm_parameter" "parameter-service-affecting-daily-bandwidth-report-enabled-customers-per-host" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-affecting/daily-bandwidth-report/enabled-customers-per-host"
  description = "Mapping of VeloCloud hosts and Bruin customer IDs for whom this report will trigger periodically"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "DAILY_BANDWIDTH_REPORT__ENABLED_CUSTOMERS_PER_HOST"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-affecting-daily-bandwidth-report-execution-cron-expression" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-affecting/daily-bandwidth-report/execution-cron-expression"
  description = "Cron expression that determines when to build and deliver this report"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "DAILY_BANDWIDTH_REPORT__EXECUTION_CRON_EXPRESSION"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-affecting-daily-bandwidth-report-lookup-interval" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-affecting/daily-bandwidth-report/lookup-interval"
  description = "Defines how much time back to look for bandwidth metrics and Bruin tickets"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "DAILY_BANDWIDTH_REPORT__LOOKUP_INTERVAL"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-affecting-daily-bandwidth-report-recipients" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-affecting/daily-bandwidth-report/recipients"
  description = "List of recipients that will get these reports"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "DAILY_BANDWIDTH_REPORT__RECIPIENTS"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-affecting-monitor-autoresolve-lookup-interval" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-affecting/monitor/autoresolve-lookup-interval"
  description = "Defines how much time back to look for all kinds of metrics while running auto-resolves"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MONITORING__AUTORESOLVE_LOOKUP_INTERVAL"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-affecting-monitor-bandwidth-over-utilization-monitoring-lookup-interval" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-affecting/monitor/bandwidth-over-utilization-monitoring-lookup-interval"
  description = "Defines how much time back to look for Bandwidth metrics in Bandwidth Over Utilization checks"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MONITORING__BANDWIDTH_OVER_UTILIZATION_MONITORING_LOOKUP_INTERVAL"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-affecting-monitor-bandwidth-over-utilization-monitoring-threshold" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-affecting/monitor/bandwidth-over-utilization-monitoring-threshold"
  description = "Threshold for Bandwidth Over Utilization troubles"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MONITORING__BANDWIDTH_OVER_UTILIZATION_MONITORING_THRESHOLD"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-affecting-monitor-circuit-instability-autoresolve-threshold" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-affecting/monitor/circuit-instability-autoresolve-threshold"
  description = "Max DOWN events allowed in Circuit Instability checks while auto-resolving tickets"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MONITORING__CIRCUIT_INSTABILITY_AUTORESOLVE_THRESHOLD"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-affecting-monitor-circuit-instability-monitoring-lookup-interval" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-affecting/monitor/circuit-instability-monitoring-lookup-interval"
  description = "Mapping of VeloCloud hosts and Bruin customer IDs for whom this report will trigger periodically"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MONITORING__CIRCUIT_INSTABILITY_MONITORING_LOOKUP_INTERVAL"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-affecting-monitor-circuit-instability-monitoring-threshold" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-affecting/monitor/circuit-instability-monitoring-threshold"
  description = "Threshold for Circuit Instability troubles"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MONITORING__CIRCUIT_INSTABILITY_MONITORING_THRESHOLD"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-affecting-monitor-customers-to-always-use-default-contact-info" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-affecting/monitor/customers-to-always-use-default-contact-info"
  description = "[Monitoring] List Bruin customers that should always use the default contact info"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MONITORING__CUSTOMERS_TO_ALWAYS_USE_DEFAULT_CONTACT_INFO"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-affecting-monitor-customers-with-bandwidth-over-utilization-monitoring" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-affecting/monitor/customers-with-bandwidth-over-utilization-monitoring"
  description = "List of client IDs for which Bandwidth Over Utilization checks are enabled"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MONITORING__CUSTOMERS_WITH_BANDWIDTH_MONITORING_ENABLED"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-affecting-monitor-default-contact-info-per-customer" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-affecting/monitor/default-contact-info-per-customer"
  description = "Mapping of VeloCloud hosts, Bruin customers and default contact info"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name
  tier        = "Advanced"

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MONITORING__DEFAULT_CONTACT_INFO_PER_CUSTOMER"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-affecting-monitor-grace-period-to-autoresolve-after-last-documented-trouble-day-time" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-affecting/monitor/grace-period-to-autoresolve-after-last-documented-trouble-day-time"
  description = "Defines for how long a ticket can be auto-resolved after the last documented trouble during the day"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MONITORING__GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_TROUBLE_DAY_TIME"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-affecting-monitor-grace-period-to-autoresolve-after-last-documented-trouble-night-time" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-affecting/monitor/grace-period-to-autoresolve-after-last-documented-trouble-night-time"
  description = "Defines for how long a ticket can be auto-resolved after the last documented trouble during the night"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MONITORING__GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_TROUBLE_NIGHT_TIME"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-affecting-monitor-jitter-monitoring-lookup-interval" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-affecting/monitor/jitter-monitoring-lookup-interval"
  description = "Defines how much time back to look for Jitter metrics in Jitter checks"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MONITORING__JITTER_MONITORING_LOOKUP_INTERVAL"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-affecting-monitor-jitter-monitoring-threshold" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-affecting/monitor/jitter-monitoring-threshold"
  description = "Threshold for Jitter troubles"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MONITORING__JITTER_MONITORING_THRESHOLD"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-affecting-monitor-latency-monitoring-lookup-interval" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-affecting/monitor/latency-monitoring-lookup-interval"
  description = "Defines how much time back to look for Latency metrics in Latency checks"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MONITORING__LATENCY_MONITORING_LOOKUP_INTERVAL"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-affecting-monitor-latency-monitoring-threshold" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-affecting/monitor/latency-monitoring-threshold"
  description = "Threshold for Latency troubles"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MONITORING__LATENCY_MONITORING_THRESHOLD"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-affecting-monitor-link-labels-blacklisted-in-asr-forwards" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-affecting/monitor/link-labels-blacklisted-in-asr-forwards"
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

resource "aws_ssm_parameter" "parameter-service-affecting-monitor-link-labels-blacklisted-in-hnoc-forwards" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-affecting/monitor/link-labels-blacklisted-in-hnoc-forwards"
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

resource "aws_ssm_parameter" "parameter-service-affecting-monitor-max-autoresolves-per-ticket" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-affecting/monitor/max-autoresolves-per-ticket"
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

resource "aws_ssm_parameter" "parameter-service-affecting-monitor-monitored-velocloud-hosts" {
  name        = "/automation-engine/${local.env}/service-affecting/monitor/monitored-velocloud-hosts"
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
    Name = "MONITORING__MONITORED_VELOCLOUD_HOSTS"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-affecting-monitor-monitoring-job-interval" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-affecting/monitor/monitoring-job-interval"
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

resource "aws_ssm_parameter" "parameter-service-affecting-monitor-packet-loss-monitoring-lookup-interval" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-affecting/monitor/packet-loss-monitoring-lookup-interval"
  description = "Defines how much time back to look for Packet Loss metrics in Packet Loss checks"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MONITORING__PACKET_LOSS_MONITORING_LOOKUP_INTERVAL"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-affecting-monitor-packet-loss-monitoring-threshold" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-affecting/monitor/packet-loss-monitoring-threshold"
  description = "Threshold for Packet Loss troubles"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "MONITORING__PACKET_LOSS_MONITORING_THRESHOLD"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-affecting-monitored-product-category" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-affecting/monitored-product-category"
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

resource "aws_ssm_parameter" "parameter-service-affecting-monitor-wait-time-before-sending-new-milestone-reminder" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-affecting/monitor/wait-time-before-sending-new-milestone-reminder"
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

resource "aws_ssm_parameter" "parameter-service-affecting-reoccurring-trouble-report-execution-cron-expression" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-affecting/reoccurring-trouble-report/execution-cron-expression"
  description = "Cron expression that determines when to build and deliver this report"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "REOCCURRING_TROUBLE_REPORT__RECIPIENTS_PER_CUSTOMER"
    note = "can be updated from the parameter store dashboard"
  })
}
resource "aws_ssm_parameter" "parameter-service-affecting-reoccurring-trouble-report-default-contacts" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-affecting/reoccurring-trouble-report/default-contacts"
  description = "List of default contacts to whom this report will always be delivered to"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "REOCCURRING_TROUBLE_REPORT__DEFAULT_CONTACTS"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-affecting-reoccurring-trouble-report-recipients-per-host-and-customer" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-affecting/reoccurring-trouble-report/recipients-per-host-and-customer"
  description = "Mapping of VeloCloud hosts, Bruin customer IDs and recipients of these reports"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "REOCCURRING_TROUBLE_REPORT__RECIPIENTS_PER_HOST_AND_CUSTOMER"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-affecting-reoccurring-trouble-report-reoccurring-trouble-tickets-threshold" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-affecting/reoccurring-trouble-report/reoccurring-trouble-tickets-threshold"
  description = "Number of different tickets a trouble must appear in for a particular edge and interface to include it in the report"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "REOCCURRING_TROUBLE_REPORT__REOCCURRING_TROUBLE_TICKETS_THRESHOLD"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-affecting-reoccurring-trouble-report-reported-troubles" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-affecting/reoccurring-trouble-report/reported-troubles"
  description = "Troubles that will be reported"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "REOCCURRING_TROUBLE_REPORT__REPORTED_TROUBLES"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-service-affecting-reoccurring-trouble-report-tickets-lookup-interval" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/service-affecting/reoccurring-trouble-report/tickets-lookup-interval"
  description = "Defines how much time back to look for Bruin tickets"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "REOCCURRING_TROUBLE_REPORT__TICKETS_LOOKUP_INTERVAL"
    note = "can be updated from the parameter store dashboard"
  })
}

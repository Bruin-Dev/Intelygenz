resource "aws_ssm_parameter" "parameter-customer-cache-blacklisted-clients-with-pending-status" {
  name        = "/automation-engine/${local.env}/customer-cache/blacklisted-clients-with-pending-status"
  description = "Client IDs whose edges have Pending management status that should be ignored in the caching process"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "BLACKLISTED_CLIENTS_WITH_PENDING_STATUS"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-customer-cache-blacklisted-edges" {
  name        = "/automation-engine/${local.env}/customer-cache/blacklisted-edges"
  description = "VeloCloud edges that should be ignored in the caching process"
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

resource "aws_ssm_parameter" "parameter-customer-cache-duplicate-inventories-recipient" {
  name        = "/automation-engine/${local.env}/customer-cache/duplicate-inventories-recipient"
  description = "E-mail address that will get e-mails with a relation of service numbers that have multiple Bruin inventories"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "DUPLICATE_INVENTORIES_RECIPIENT"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-customer-cache-refresh-check-interval" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/customer-cache/refresh-check-interval"
  description = "Defines how often the next refresh flag is checked to decide if it's time to refresh the cache or not"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "REFRESH_CHECK_INTERVAL"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-customer-cache-refresh-job-interval" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/customer-cache/refresh-job-interval"
  description = "Defines how often the cache is refreshed"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "REFRESH_JOB_INTERVAL"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-customer-cache-velocloud-hosts" {
  name        = "/automation-engine/${local.env}/customer-cache/velocloud-hosts"
  description = "VeloCloud hosts whose edges will be stored to the cache"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "VELOCLOUD_HOSTS"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-customer-cache-whitelisted-management-statuses" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/customer-cache/whitelisted-management-statuses"
  description = "Management statuses that should be considered in the caching process"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "WHITELISTED_MANAGEMENT_STATUSES"
    note = "can be updated from the parameter store dashboard"
  })
}

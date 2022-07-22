resource "aws_ssm_parameter" "parameter-hawkeye-customer-cache-duplicate-inventories-recipient" {
  name        = "/automation-engine/${local.env}/hawkeye-customer-cache/duplicate-inventories-recipient"
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

resource "aws_ssm_parameter" "parameter-hawkeye-customer-cache-refresh-job-interval" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/hawkeye-customer-cache/refresh-job-interval"
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

resource "aws_ssm_parameter" "parameter-hawkeye-customer-cache-whitelisted-management-statuses" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/hawkeye-customer-cache/whitelisted-management-statuses"
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

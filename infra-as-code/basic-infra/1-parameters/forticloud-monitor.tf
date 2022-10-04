resource "aws_ssm_parameter" "parameter-forticloud-monitor-base-url" {
  name        = "/automation-engine/${local.env}/forticloud-monitor/base-url"
  description = "Base URL for Bruin's API"
  type        = "SecureString"
  value       = ""  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "BRUIN_BASE_URL"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-forticloud-monitor-login-url" {
  name        = "/automation-engine/${local.env}/forticloud-monitor/login-url"
  description = "Login URL for Bruin's API"
  type        = "SecureString"
  value       = ""  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "BRUIN_LOGIN_URL"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-forticloud-monitor-client-id" {
  name        = "/automation-engine/${local.env}/forticloud-monitor/client-id"
  description = "Client ID credential to authenticate against Bruin's API"
  type        = "SecureString"
  value       = ""  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "BRUIN_CLIENT_ID"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-forticloud-monitor-client-secret" {
  name        = "/automation-engine/${local.env}/forticloud-monitor/client-secret"
  description = "Client Secret credential to authenticate against Bruin's API"
  type        = "SecureString"
  value       = ""  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "BRUIN_CLIENT_SECRET"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-forticloud-base-url" {
  name        = "/automation-engine/${local.env}/forticloud/base-url"
  description = "Base URL for the Forticloud API"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "FORTICLOUD_BASE_URL"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-forticloud-username" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/forticloud/username"
  description = "User for the Forticloud API"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "FORTICLOUD_USERNAME"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-forticloud-password" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/forticloud/password"
  description = "Password for the Forticloud API"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "FORTICLOUD_PASSWORD"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-forticloud-account" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/forticloud/account"
  description = "Account for the Forticloud API"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "FORTICLOUD_ACCOUNT"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-bruin-base-url" {
  name        = "/automation-engine/${local.env}/bruin/base-url"
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


resource "aws_ssm_parameter" "parameter-bruin-client-id" {
  name        = "/automation-engine/${local.env}/bruin/client-id"
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

resource "aws_ssm_parameter" "parameter-bruin-client-secret" {
  name        = "/automation-engine/${local.env}/bruin/client-secret"
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

resource "aws_ssm_parameter" "parameter-bruin-login-url" {
  name        = "/automation-engine/${local.env}/bruin/login-url"
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
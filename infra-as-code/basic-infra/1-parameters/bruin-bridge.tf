resource "aws_ssm_parameter" "parameter-bruin-bridge-base-url" {
  name        = "/automation-engine/${local.env}/bruin-bridge/base-url"
  description = "Base URL for Bruin's API"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
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


resource "aws_ssm_parameter" "parameter-bruin-bridge-base-url-ip" {
  name        = "/automation-engine/${local.env}/bruin-bridge/base-url-ip"
  description = "IP address where Bruin's API can be reached"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "BRUIN_BASE_URL_IP"
    note = "can be updated from the parameter store dashboard"
  })
}


resource "aws_ssm_parameter" "parameter-bruin-bridge-test-base-url" {
  name        = "/automation-engine/${local.env}/bruin-bridge/test-base-url"
  description = "Base URL for Bruin's TEST API"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "BRUIN_TEST_BASE_URL"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-bruin-bridge-client-id" {
  name        = "/automation-engine/${local.env}/bruin-bridge/client-id"
  description = "Client ID credential to authenticate against Bruin's API"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
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

resource "aws_ssm_parameter" "parameter-bruin-bridge-client-secret" {
  name        = "/automation-engine/${local.env}/bruin-bridge/client-secret"
  description = "Client Secret credential to authenticate against Bruin's API"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
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

resource "aws_ssm_parameter" "parameter-bruin-bridge-login-url" {
  name        = "/automation-engine/${local.env}/bruin-bridge/login-url"
  description = "Login URL for Bruin's API"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
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

resource "aws_ssm_parameter" "parameter-bruin-bridge-test-login-url" {
  name        = "/automation-engine/${local.env}/bruin-bridge/test-login-url"
  description = "Login URL for Bruin's TEST API"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "BRUIN_TEST_LOGIN_URL"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-bruin-bridge-login-url-ip" {
  name        = "/automation-engine/${local.env}/bruin-bridge/login-url-ip"
  description = "IP address where Bruin's Login Server can be reached"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "BRUIN_LOGIN_URL_IP"
    note = "can be updated from the parameter store dashboard"
  })
}
resource "aws_ssm_parameter" "parameter-bruin-bridge-test-client-id" {
  name        = "/automation-engine/${local.env}/bruin-bridge/test-client-id"
  description = "Client ID credential to authenticate against Bruin's TEST API"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "BRUIN_TEST_CLIENT_ID"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-bruin-bridge-test-client-secret" {
  name        = "/automation-engine/${local.env}/bruin-bridge/test-client-secret"
  description = "Client secret credential to authenticate against Bruin's TEST API"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "BRUIN_TEST_CLIENT_SECRET"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-digi-bridge-digi-reboot-api-base-url" {
  name        = "/automation-engine/${local.env}/digi-bridge/digi-reboot-api-base-url"
  description = "Base URL for Digi API"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "DIGI_BASE_URL"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-digi-bridge-digi-reboot-api-client-id" {
  name        = "/automation-engine/${local.env}/digi-bridge/digi-reboot-api-client-id"
  description = "Client ID credentials for Digi API"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "DIGI_CLIENT_ID"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-digi-bridge-digi-reboot-api-client-secret" {
  name        = "/automation-engine/${local.env}/digi-bridge/digi-reboot-api-client-secret"
  description = "Client Secret credentials for Digi API"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "DIGI_CLIENT_SECRET"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-digi-bridge-digi-reboot-api-token-ttl" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/digi-bridge/digi-reboot-api-token-ttl"
  description = "Auth tokens TTL"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "DIGI_TOKEN_TTL"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-digi-bridge-digi-headers" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/digi-bridge/digi-headers"
  description = "List of possible headers included in all DiGi links"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "DIGI_HEADERS"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-digi-bridge-digi-reboot-api-ip" {
  name        = "/automation-engine/${local.env}/digi-bridge/digi-reboot-api-ip"
  description = "IP for Digi Environment"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "DIGI_API_IP"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-digi-bridge-digi-reboot-api-test-ip" {
  name        = "/automation-engine/${local.env}/digi-bridge/digi-reboot-api-test-ip"
  description = "IP for Digi Test Environment"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "DIGI_API_TEST_IP"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-digi-bridge-digi-reboot-api-dns-record-name" {
  name        = "/automation-engine/${local.env}/digi-bridge/digi-reboot-api-dns-record-name"
  description = "Client Secret credentials for Digi API"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "DIGI_DNS_RECORD_NAME"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "parameter-digi-bridge-digi-reboot-api-test-dns-record-name" {
  name        = "/automation-engine/${local.env}/digi-bridge/digi-reboot-api-test-dns-record-name"
  description = "Client Secret credentials for Digi API"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "DIGI_TEST_DNS_RECORD_NAME"
    note = "can be updated from the parameter store dashboard"
  })
}

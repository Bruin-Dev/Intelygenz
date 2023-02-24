
resource "aws_ssm_parameter" "service-affecting-s3-service-account-access-key" {
  name        = "/automation-engine/${var.environment}/service-affecting/s3-serving-affecting-iam-user-access-key"
  description = "Secret key of serving affecting monitor service account to access the s3 bucket with the same name(Automatic value, don´t update it manually)."
  type        = "SecureString"
  value       = var.service_affecting_monitor_s3_access_key
  key_id      = var.global_ssm_kms_name

  tags = merge(var.common_info, {
    Name = "SERVICE_AFFECTING_MONITOR_S3_IAM_SERVICE_ACCOUNT_ACCESS_KEY"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "service-affecting-s3-service-account-secret-key" {
  name        = "/automation-engine/${var.environment}/service-affecting/s3-serving-affecting-iam-user-secret-key"
  description = "Secret key of serving affecting monitor service account to access the s3 bucket with the same name(Automatic value, don´t update it manually)."
  type        = "SecureString"
  value       = var.service_affecting_monitor_s3_secret_key
  key_id      = var.global_ssm_kms_name

  tags = merge(var.common_info, {
    Name = "SERVICE_AFFECTING_MONITOR_S3_IAM_SERVICE_ACCOUNT_SECRET_KEY"
    note = "can be updated from the parameter store dashboard"
  })
}

resource "aws_ssm_parameter" "service-affecting-s3-bucket-name" {
  name        = "/automation-engine/${var.environment}/service-affecting/s3-bucket-name"
  description = "serving affecting monitor s3 bucket name (Automatic value, don´t update it manually)."
  type        = "SecureString"
  value       = var.service_affecting_monitor_s3_bucket_name
  key_id      = var.global_ssm_kms_name

  tags = merge(var.common_info, {
    Name = "SERVICE_AFFECTING_MONITOR_S3_BUCKET_NAME"
    note = "can be updated from the parameter store dashboard"
  })
}
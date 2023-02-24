data "aws_kms_key" "ssm-kms-key" {
  key_id = "alias/kms-key-${var.CURRENT_ENVIRONMENT}-parameters"
}


module "service_affecting_monitor" {
  source                                   = "./modules/services/service-affecting-monitor"
  common_info                              = var.common_info
  service_affecting_monitor_s3_bucket_name = aws_s3_bucket.service_affecting_monitor.bucket
  service_affecting_monitor_s3_access_key  = aws_iam_access_key.service_affecting_monitor_s3.id
  service_affecting_monitor_s3_secret_key  = aws_iam_access_key.service_affecting_monitor_s3.secret
  global_ssm_kms_name                      = data.aws_kms_key.ssm-kms-key.id
}

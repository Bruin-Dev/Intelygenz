locals = {
  service_affecting_monitor_s3_name = "service-affecting-monitor-${var.CURRENT_ENVIRONMENT}"
}

resource "aws_s3_bucket" "service_affecting_monitor" {
  bucket        = local.service_affecting_monitor_s3_name
  acl           = "private"
  force_destroy = true

  tags = {
    Name         = local.service_affecting_monitor_s3_name
    Environment  = var.CURRENT_ENVIRONMENT
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "service_affecting_monitor" {
  bucket = aws_s3_bucket.service_affecting_monitor.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.s3.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

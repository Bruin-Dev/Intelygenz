resource "aws_s3_bucket" "bucket_eks_cluster" {
  bucket        = local.bucket_eks_name
  acl           = "private"
  force_destroy = true

  tags = {
    Name         = local.bucket_eks_name
    Environment  = var.CURRENT_ENVIRONMENT
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
  }
}

resource "aws_s3_bucket" "bucket_logs" {
  count         = var.CURRENT_ENVIRONMENT == "production" ? 1 : 0
  bucket        = local.bucket_logs_name
  acl           = "private"
  force_destroy = true

  tags = {
    Name         = local.bucket_logs_name
    Environment  = var.CURRENT_ENVIRONMENT
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
  }
}
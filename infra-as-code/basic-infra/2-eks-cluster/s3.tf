resource "aws_s3_bucket_object" "pem_file" {
  bucket  = local.bucket_name
  key     = "${local.ssh_key_name}.pem"
  content = tls_private_key.tls_private_key_eks.private_key_pem

  tags = merge(local.common_tags, {
    Name    = "${local.cluster_name}.pem"
  })
}

resource "aws_s3_bucket" "bucket_chartmuseum" {
  count         = var.CURRENT_ENVIRONMENT == "production" ? 1 : 0
  bucket        = local.chartmuseum_bucket_name
  acl           = "private"
  force_destroy = true

  tags = {
    Name         = local.chartmuseum_bucket_name
    Environment  = var.CURRENT_ENVIRONMENT
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
  }
}
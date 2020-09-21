resource "aws_s3_bucket" "bucket" {
  bucket = local.bucket_name
  acl    = "private"
  force_destroy = true

  tags = {
    Name = local.bucket_name
    Environment  = terraform.workspace
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
  }
}

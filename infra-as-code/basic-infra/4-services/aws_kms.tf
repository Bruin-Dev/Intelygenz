resource "aws_kms_key" "s3" {
  description             = "s3-encriptation-key-${var.CURRENT_ENVIRONMENT}"
  deletion_window_in_days = 10
}
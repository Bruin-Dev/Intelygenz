resource "aws_kms_key" "kms_key" {
  description             = "This key is used to encrypt ${local.env} parameters"
  deletion_window_in_days = 10

  tags = merge(var.common_info, {
    Name = "kms-key-${local.env}-parameters"
  })
}

resource "aws_kms_alias" "kms_key" {
  name          = "alias/kms-key-${local.env}-parameters"
  target_key_id = aws_kms_key.kms_key.key_id
}

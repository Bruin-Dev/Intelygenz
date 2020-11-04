data "aws_iam_policy_document" "s3_allow_ses_puts" {
  statement {
    sid    = "allow-ses-puts"
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["ses.amazonaws.com"]
    }

    actions = [
      "s3:PutObject",
    ]

    resources = [
      "arn:aws:s3:::${local.ses_bucket_name}/${local.ses_bucket_prefix}/*",
    ]

    condition {
      test     = "StringEquals"
      variable = "aws:Referer"
      values   = [data.aws_caller_identity.current.account_id]
    }
  }
}

resource "aws_s3_bucket" "temp_bucket" {
  bucket        = local.ses_bucket_name
  acl           = "private"
  force_destroy = true
  policy        = data.aws_iam_policy_document.s3_allow_ses_puts.json

  tags = {
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
  }
}

resource "aws_s3_bucket_public_access_block" "public_access_block" {
  bucket = aws_s3_bucket.temp_bucket.id

  # Block new public ACLs and uploading public objects
  block_public_acls = true

  # Retroactively remove public access granted through public ACLs
  ignore_public_acls = true

  # Block new public bucket policies
  block_public_policy = true

  # Retroactivley block public and cross-account access if bucket has public policies
  restrict_public_buckets = true
}
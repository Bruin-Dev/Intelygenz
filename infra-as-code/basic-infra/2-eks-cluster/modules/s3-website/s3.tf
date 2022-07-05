resource "aws_s3_bucket" "s3_bucket_website" {
  bucket = "${var.prefix}-website-${var.environment}"
  acl    = "private"

  website {
    index_document = var.index_document
    error_document = var.error_document
  }

  tags = {
    Name        = "${var.prefix}-website-${var.environment}"
    Environment = var.environment
  }
}

data "aws_iam_policy_document" "cloudfront_policy_website" {
  statement {
    sid       = "Allow get requests only from WhitelistIP"
    effect    = "Allow"
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.s3_bucket_website.arn}/*"]

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    condition {
      test     = "IpAddress"
      variable = "aws:SourceIp"
      values   = var.vpn_remote_ipset[*].value
    }
  }  

  statement {
    sid       = "Allow get requests originating from docs site"
    effect    = "Allow"
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.s3_bucket_website.arn}/*"]

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    condition {
      test     = "StringLike"
      variable = "aws:Referer"
      values   = [var.referer_header]
    }
  }

  # when the origin is S3, no valid for custom.
  # statement {
  #   effect    = "Deny"
  #   actions   = ["s3:GetObject"]
  #   resources = ["${aws_s3_bucket.s3_bucket_website.arn}/*"]

  #   not_principals {
  #     type        = "AWS"
  #     identifiers = [aws_cloudfront_origin_access_identity.access_identity_website.iam_arn]
  #   }
  # }

  # statement {
  #   effect    = "Allow"
  #   actions   = ["s3:GetObject"]
  #   resources = ["${aws_s3_bucket.s3_bucket_website.arn}/*"]

  #   principals {
  #     type        = "AWS"
  #     identifiers = [aws_cloudfront_origin_access_identity.access_identity_website.iam_arn]
  #   }
  # }

  # statement {
  #   effect    = "Allow"
  #   actions   = ["s3:ListBucket"]
  #   resources = [aws_s3_bucket.s3_bucket_website.arn]

  #   principals {
  #     type        = "AWS"
  #     identifiers = [aws_cloudfront_origin_access_identity.access_identity_website.iam_arn]
  #   }
  # }
}

resource "aws_s3_bucket_policy" "cloudfront_policy_website" {
  bucket = aws_s3_bucket.s3_bucket_website.id
  policy = data.aws_iam_policy_document.cloudfront_policy_website.json
}
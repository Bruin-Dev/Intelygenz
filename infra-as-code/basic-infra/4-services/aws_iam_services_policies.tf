data "aws_iam_policy_document" "service_affecting_monitor_s3" {
  statement {
    actions = [
      "s3:*",
    ]

    principals {
      type = "AWS"
      identifiers = [
        "arn:aws:iam::374050862540:group/Automation"
      ]
    }

    resources = [
      "arn:aws:s3:::${aws_s3_bucket.service_affecting_monitor.bucket}/",
      "arn:aws:s3:::${aws_s3_bucket.service_affecting_monitor.bucket}/*",
    ]
  }

  statement {
    actions = [
      "s3:PutObject",
    ]

    principal = [

    ]
    principals {
      type = "AWS"
      identifiers = [
        "arn:aws:iam::${data.aws_caller_identity.current.account_id}:user/${aws_iam_user.service_affecting_monitor_s3.bucket}",
      ]
    }
    resources = [
      "arn:aws:s3:::${aws_s3_bucket.service_affecting_monitor.bucket}/",
      "arn:aws:s3:::${aws_s3_bucket.service_affecting_monitor.bucket}/*",
    ]
  }
}

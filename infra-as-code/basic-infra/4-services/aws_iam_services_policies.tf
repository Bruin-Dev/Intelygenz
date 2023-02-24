data "aws_iam_policy_document" "service_affecting_monitor_s3" {
  statement {
    actions = [
      "s3:PutObject",
    ]
    resources = [
      "arn:aws:s3:::${aws_s3_bucket.service_affecting_monitor.bucket}/",
      "arn:aws:s3:::${aws_s3_bucket.service_affecting_monitor.bucket}/*",
    ]
  }
}

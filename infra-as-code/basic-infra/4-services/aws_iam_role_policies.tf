data "aws_iam_role" "automation" {
  name = "Automation"
}

resource "aws_iam_role_policy" "test_policy" {
  name   = "s3_service_affecting_monitor"
  role   = data.aws_iam_role.automation.id
  policy = data.aws_iam_policy_document.service_affecting_monitor_s3_role.json
}

data "aws_iam_policy_document" "service_affecting_monitor_s3_role" {
  statement {
    actions = [
      "s3:*",
    ]

    resources = [
      "arn:aws:s3:::${aws_s3_bucket.service_affecting_monitor.bucket}/",
      "arn:aws:s3:::${aws_s3_bucket.service_affecting_monitor.bucket}/*",
    ]
  }
}

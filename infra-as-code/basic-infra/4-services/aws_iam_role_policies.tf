
data "aws_iam_group" "automation" {
  group_name = "Automation"
}

resource "aws_iam_group_policy" "automation_policy" {
  name   = "s3_service_affecting_monitor"
  group   = data.aws_iam_group.automation.id
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

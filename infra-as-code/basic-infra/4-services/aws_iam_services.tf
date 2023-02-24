resource "aws_iam_user" "service_affecting_monitor_s3" {
  name = local.service_affecting_monitor_s3_name
  path = "/automation/"

  tags = {
    Name         = local.bucket_chartmuseum_name
    Environment  = var.CURRENT_ENVIRONMENT
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
  }
}

resource "aws_iam_access_key" "service_affecting_monitor_s3" {
  user = aws_iam_user.service_affecting_monitor_s3.name
}

resource "aws_iam_user_policy" "service_affecting_monitor_s3" {
  name   = local.service_affecting_monitor_s3_name
  user   = aws_iam_user.service_affecting_monitor_s3.name
  policy = data.aws_iam_policy_document.service_affecting_monitor_s3.json
}

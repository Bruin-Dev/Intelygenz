resource "aws_cloudwatch_log_group" "mettel-automation" {
  name = "${var.environment}"
  retention_in_days = 30

  tags {
    Environment = "${var.environment}"
    Application = "${var.environment}"
  }
}
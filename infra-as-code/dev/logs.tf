resource "aws_cloudwatch_log_group" "automation" {
  name = "${var.ENVIRONMENT}"
  retention_in_days = 30

  tags = {
    Environment = "${var.ENVIRONMENT}"
    Application = "${var.ENVIRONMENT}"
  }
}
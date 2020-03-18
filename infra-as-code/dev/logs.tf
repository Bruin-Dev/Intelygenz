resource "aws_cloudwatch_log_group" "automation" {
  name = var.ENVIRONMENT
  retention_in_days = var.LOGS_RETENTION_PERIOD[var.CURRENT_ENVIRONMENT]

  tags = {
    Environment = var.ENVIRONMENT
    Application = var.ENVIRONMENT
  }
}
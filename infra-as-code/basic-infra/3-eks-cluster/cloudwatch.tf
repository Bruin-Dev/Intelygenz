resource "aws_cloudwatch_log_group" "eks_log_group" {
  count             = var.ENABLE_FLUENT_BIT ? 1 : 0
  name              = local.logs_name
  retention_in_days = 30
}
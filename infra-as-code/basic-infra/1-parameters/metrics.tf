resource "aws_ssm_parameter" "parameter-metrics-relevant-clients" {
  count       = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0   # -> use this to deploy a "common" parameter only in one environment, if not when merging to master will fail for duplicity
  name        = "/automation-engine/common/metrics/relevant-clients"
  description = "List of relevant client names to use on Prometheus metrics labels"
  type        = "SecureString"
  value       = "-"  # to edit go to parameter store dashboard.
  key_id      =  aws_kms_alias.kms_key.name

  lifecycle {
    ignore_changes = [
      value,
    ]
  }

  tags = merge(var.common_info, {
    Name = "METRICS_RELEVANT_CLIENTS"
    note = "can be updated from the parameter store dashboard"
  })
}

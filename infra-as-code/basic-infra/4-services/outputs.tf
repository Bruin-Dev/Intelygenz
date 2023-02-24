# This outputs have custom definition because can be empty and terraform will not fail:
# https://github.com/hashicorp/terraform/issues/23222

output "fluent-bit-role-arn" {
  value = join("", aws_iam_role.fluent-bit-role-eks.*.arn)
}

output "fluent-bit-log-group-name" {
  value = join("", aws_cloudwatch_log_group.eks_log_group.*.id)
}

output "oreilly-security-group-id" {
  description = "Oreilly whitelisted security group access"
  value       = aws_security_group.links_metrics_api_oreilly.id
}


###############################
# S3 Service Affecting Monitor
###############################
output "service-affecting-monitor-s3-name" {
  description = "Service Affecting monitor S3 Name"
  value       = aws_s3_bucket.service_affecting_monitor.name
  sensitive   = true
}

output "service-affecting-monitor-iam-access-key" {
  description = "Service account Service Affecting monitor Access key"
  value       = aws_iam_access_key.service_affecting_monitor_s3.id
  sensitive   = true
}

output "service-affecting-monitor-iam-secret-key" {
  description = "Service account Service Affecting monitor Secret key"
  value       = aws_iam_access_key.service_affecting_monitor_s3.secret
  sensitive   = true
}

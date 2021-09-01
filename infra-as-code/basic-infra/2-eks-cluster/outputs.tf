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

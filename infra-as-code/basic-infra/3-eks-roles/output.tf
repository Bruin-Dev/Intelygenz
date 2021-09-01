output "eks_developer_roles" {
  description = "List of developer users roles"
  value = aws_iam_role.developer_eks.*.arn
}

output "eks_devops_roles" {
  description = "List of devops users roles"
  value = aws_iam_role.devops_eks.*.arn
}

output "ssl-certificate-arn" {
  description = "AWS SSL certificate for automation-engine.net"
  value = aws_acm_certificate.ssl_certificate.arn
}

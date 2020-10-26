output "eks_developer_roles" {
  description = "List of developer users roles"
  value = aws_iam_role.developer_eks.*.arn
}

output "eks_developer_ops_privileged_roles" {
  description = "List of developer-ops-privileged users roles"
  value = aws_iam_role.developer_ops_privileged_eks.*.arn
}

output "eks_devops_roles" {
  description = "List of devops users roles"
  value = aws_iam_role.devops_eks.*.arn
}
data "aws_iam_user" "igz_developer_users" {
  count = length(var.eks_developer_users)
  user_name = var.eks_developer_users[count.index]
}

data "aws_iam_user" "igz_devops_users" {
  count = length(var.eks_devops_users)
  user_name = var.eks_devops_users[count.index]
}
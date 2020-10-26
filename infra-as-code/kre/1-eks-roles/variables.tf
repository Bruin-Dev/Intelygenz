variable "eks_developer_users" {
  description = "List of users with developer role access in EKS cluster"
  type    = list(string)
  default = [
    "brandon.samudio",
    "daniel.fernandez",
    "joseluis.vega",
    "sancho.munoz",
  ]
}

variable "eks_developer_ops_privileged_users" {
  description = "List of users with developer-ops-privileged role access in EKS cluster"
  type = list(string)
  default = [
    "xisco.capllonch",
    "xoan.mallon.developer"
  ]
}

variable "eks_devops_users" {
  description = "List of users with devops role access in EKS cluster"
  type    = list(string)
  default = [
    "alberto.iglesias",
    "angel.costales",
    "angel.luis.piquero",
    "xoan.mallon.devops"
  ]
}

data "aws_iam_user" "igz_developer_users" {
  count = length(var.eks_developer_users)
  user_name = var.eks_developer_users[count.index]
}

data "aws_iam_user" "igz_developer_ops_users" {
  count = length(var.eks_developer_ops_privileged_users)
  user_name = var.eks_developer_ops_privileged_users[count.index]
}

data "aws_iam_user" "igz_devops_users" {
  count = length(var.eks_devops_users)
  user_name = var.eks_devops_users[count.index]
}
data "template_file" "developer_ops_privileged_eks_role" {
  count    = length(var.eks_developer_ops_privileged_users)
  template = file("${path.module}/policies/user-role.json")
  vars = {
    user_name = var.eks_developer_ops_privileged_users[count.index]
  }
}

resource "aws_iam_role" "developer_ops_privileged_eks" {
  count                 = length(var.eks_developer_ops_privileged_users)
  name                  = "eks-developer-ops-${var.common_info.project}-${var.eks_developer_ops_privileged_users[count.index]}"
  assume_role_policy    = data.template_file.developer_ops_privileged_eks_role[count.index].rendered
  force_detach_policies = true
  tags = {
    Project-Role  = "developer-ops-privileged"
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    User          = var.eks_developer_ops_privileged_users[count.index]
  }
}

data "template_file" "assume-developer-ops-role" {
  count   = length(var.eks_developer_ops_privileged_users)
  template = file("${path.module}/policies/assume-role-policy.json")

  vars = {
    resource_arn = aws_iam_role.developer_ops_privileged_eks[count.index].arn
  }
}

resource "aws_iam_policy" "assume-developer-ops-role" {
  count  = length(var.eks_developer_ops_privileged_users)
  name   = "policy-eks-developer-ops-${var.common_info.project}-${var.eks_devops_users[count.index]}"
  policy = data.template_file.assume-developer-ops-role[count.index].rendered
}

data "template_file" "developer-ops-role-policy" {
  count   = length(var.eks_developer_ops_privileged_users)
  template = file("${path.module}/policies/role-policy-eks.json")
}

resource "aws_iam_role_policy" "developer-ops-role-policy-permissions" {
  count = length(var.eks_developer_ops_privileged_users)
  name = "role-policy-eks-developer-ops-${var.common_info.project}-${var.eks_devops_users[count.index]}"
  role = aws_iam_role.developer_ops_privileged_eks[count.index].id

  policy = data.template_file.developer-ops-role-policy[count.index].rendered
}

resource "aws_iam_user_policy_attachment" "attach-developer-ops-user" {
  count      = length(var.eks_developer_ops_privileged_users)
  user       = data.aws_iam_user.igz_developer_ops_users[count.index].user_name
  policy_arn = aws_iam_policy.assume-developer-ops-role[count.index].arn
}
data "template_file" "developer_eks_role" {
  count    = length(var.eks_developer_users)
  template = file("${path.module}/policies/user-role.json")
  vars = {
    user_name = var.eks_developer_users[count.index]
  }
}

resource "aws_iam_role" "developer_eks" {
  count                 = length(var.eks_developer_users)
  name                  = "eks-developer-${var.common_info.project}-${var.eks_developer_users[count.index]}"
  assume_role_policy    = data.template_file.developer_eks_role[count.index].rendered
  force_detach_policies = true
  tags = {
    Project-Role  = "developer"
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    User          = var.eks_developer_users[count.index]
  }
}

data "template_file" "assume-developer-role" {
  count   = length(var.eks_developer_users)
  template = file("${path.module}/policies/assume-role-policy.json")

  vars = {
    resource_arn = aws_iam_role.developer_eks[count.index].arn
  }
}

resource "aws_iam_policy" "assume-developer-role" {
  count  = length(var.eks_developer_users)
  name   = "policy-eks-developer-${var.common_info.project}-${var.eks_developer_users[count.index]}"
  policy = data.template_file.assume-developer-role[count.index].rendered
}

data "template_file" "developer-role-policy" {
  count   = length(var.eks_developer_users)
  template = file("${path.module}/policies/role-policy-eks.json")
}

resource "aws_iam_role_policy" "developer-role-policy-permissions" {
  count = length(var.eks_developer_users)
  name = "role-policy-eks-developer-${var.common_info.project}-${var.eks_developer_users[count.index]}"
  role = aws_iam_role.developer_eks[count.index].id

  policy = data.template_file.developer-role-policy[count.index].rendered
}

resource "aws_iam_user_policy_attachment" "attach-developer-user" {
  count      = length(var.eks_developer_users)
  user       = data.aws_iam_user.igz_developer_users[count.index].user_name
  policy_arn = aws_iam_policy.assume-developer-role[count.index].arn
}
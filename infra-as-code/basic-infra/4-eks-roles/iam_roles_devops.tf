data "template_file" "devops_eks_role" {
  count    = length(var.eks_devops_users)
  template = file("${path.module}/policies/user-role.json")
  vars = {
    user_name = var.eks_devops_users[count.index]
  }
}

resource "aws_iam_role" "devops_eks" {
  count                 = length(var.eks_devops_users)
  name                  = "eks-devops-${var.common_info.project}-${var.eks_devops_users[count.index]}"
  assume_role_policy    = data.template_file.devops_eks_role[count.index].rendered
  force_detach_policies = true
  tags = {
    Project-Role  = "devops"
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    User          = var.eks_devops_users[count.index]
  }
}

data "template_file" "assume-devops-role" {
  count   = length(var.eks_devops_users)
  template = file("${path.module}/policies/assume-role-policy.json")

  vars = {
    resource_arn = aws_iam_role.devops_eks[count.index].arn
  }
}

resource "aws_iam_policy" "assume-devops-role" {
  count  = length(var.eks_devops_users)
  name   = "policy-eks-devops-${var.common_info.project}-${var.eks_devops_users[count.index]}"
  policy = data.template_file.assume-devops-role[count.index].rendered
}

data "template_file" "devops-role-policy" {
  count   = length(var.eks_devops_users)
  template = file("${path.module}/policies/role-policy-eks.json")
}

resource "aws_iam_role_policy" "devops-role-policy-permissions" {
  count = length(var.eks_devops_users)
  name = "role-policy-eks-devops-${var.common_info.project}-${var.eks_devops_users[count.index]}"
  role = aws_iam_role.devops_eks[count.index].id

  policy = data.template_file.devops-role-policy[count.index].rendered
}

resource "aws_iam_user_policy_attachment" "attach-devops-user" {
  count      = length(var.eks_devops_users)
  user       = data.aws_iam_user.igz_devops_users[count.index].user_name
  policy_arn = aws_iam_policy.assume-devops-role[count.index].arn
}
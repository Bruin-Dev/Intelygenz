locals {
  eks_cluster_oidc_issuer_arn = trim(data.aws_eks_cluster.cluster.identity[0]["oidc"][0]["issuer"], "https://")
  external-dns-role-name =  "${local.cluster_name}-external-dns-oidc"
  external-dns-policy-name = "${local.cluster_name}-external-dns-oidc-policy"
  cert-manager-role-name =  "${local.cluster_name}-cert-manager-oidc"
  cert-manager-policy-name = "${local.cluster_name}-cert-manager-oidc-policy"
  aws-ebs-csi-driver-role-name =  "${local.cluster_name}-aws-ebs-csi-driver-oidc"
  aws-ebs-csi-driver-policy-name = "${local.cluster_name}-aws-ebs-csi-driver-oidc-policy"
}


################
# EXTERNAL DNS #
################

data "template_file" "external-dns-eks-role" {
  template = file("${path.module}/roles/external-dns-role.json")

  vars = {
    eks_cluster_oidc_arn = local.eks_cluster_oidc_issuer_arn
    account_id = data.aws_caller_identity.current.account_id
  }
}

resource "aws_iam_role" "external-dns-role-eks" {
  name                  = local.external-dns-role-name
  assume_role_policy    = data.template_file.external-dns-eks-role.rendered
  force_detach_policies = true
  
  tags = {
    Environment  = terraform.workspace
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
  }
}

data "template_file" "external-dns-eks-policy" {
  template = file("${path.module}/policies/external-dns-policy.json")
}

resource "aws_iam_policy" "external-dns-eks" {
  name   = local.external-dns-policy-name
  policy = data.template_file.external-dns-eks-policy.rendered
}

resource "aws_iam_role_policy_attachment" "external-dns-eks-attachment" {
  role       = aws_iam_role.external-dns-role-eks.name
  policy_arn = aws_iam_policy.external-dns-eks.arn
}


################
# CERT MANAGER #
################

data "template_file" "cert-manager-eks-role" {
  template = file("${path.module}/roles/cert-manager-role.json")

  vars = {
    eks_cluster_oidc_arn = local.eks_cluster_oidc_issuer_arn
    account_id = data.aws_caller_identity.current.account_id
  }
}

resource "aws_iam_role" "cert-manager-role-eks" {
  name                  = local.cert-manager-role-name
  assume_role_policy    = data.template_file.cert-manager-eks-role.rendered
  force_detach_policies = true
  
  tags = {
    Environment  = terraform.workspace
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
  }
}

data "template_file" "cert-manager-eks-policy" {
  template = file("${path.module}/policies/cert-manager-policy.json")
}

resource "aws_iam_policy" "cert-manager-eks" {
  name   = local.cert-manager-policy-name
  policy = data.template_file.cert-manager-eks-policy.rendered
}

resource "aws_iam_role_policy_attachment" "cert-manager-eks-attachment" {
  role       = aws_iam_role.cert-manager-role-eks.name
  policy_arn = aws_iam_policy.cert-manager-eks.arn
}


######################
# AWS EBS CSI DRIVER #
######################

data "template_file" "aws-ebs-csi-driver-eks-role" {
  template = file("${path.module}/roles/aws-ebs-csi-driver-role.json")

  vars = {
    eks_cluster_oidc_arn = local.eks_cluster_oidc_issuer_arn
    account_id = data.aws_caller_identity.current.account_id
  }
}

resource "aws_iam_role" "aws-ebs-csi-driver-role-eks" {
  name                  = local.aws-ebs-csi-driver-role-name
  assume_role_policy    = data.template_file.aws-ebs-csi-driver-eks-role.rendered
  force_detach_policies = true
  
  tags = {
    Environment  = terraform.workspace
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
  }
}

data "template_file" "aws-ebs-csi-driver-eks-policy" {
  template = file("${path.module}/policies/aws-ebs-csi-driver-policy.json")
}

resource "aws_iam_policy" "aws-ebs-csi-driver-eks" {
  name   = local.aws-ebs-csi-driver-policy-name
  policy = data.template_file.aws-ebs-csi-driver-eks-policy.rendered
}

resource "aws_iam_role_policy_attachment" "aws-ebs-csi-driver-eks-attachment" {
  role       = aws_iam_role.aws-ebs-csi-driver-role-eks.name
  policy_arn = aws_iam_policy.aws-ebs-csi-driver-eks.arn
}

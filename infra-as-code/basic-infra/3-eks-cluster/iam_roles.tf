// IAM roles local vars
locals {
  eks_cluster_oidc_issuer_arn = trim(data.aws_eks_cluster.cluster.identity[0]["oidc"][0]["issuer"], "https://")
  external-dns-role-name =  "${local.cluster_name}-external-dns-oidc"
  external-dns-policy-name = "${local.cluster_name}-external-dns-oidc-policy"
}

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

  tags                  = local.common_tags
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
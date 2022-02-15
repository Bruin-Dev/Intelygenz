// IAM roles local vars
locals {
  eks_cluster_oidc_issuer_arn = trim(data.aws_eks_cluster.cluster.identity[0]["oidc"][0]["issuer"], "https://")
  external-dns-role-name =  "${local.cluster_name}-external-dns-oidc"
  external-dns-policy-name = "${local.cluster_name}-external-dns-oidc-policy"
  cluster-autoscaler-role-name =  "${local.cluster_name}-cluster-autoscaler-oidc"
  cluster-autoscaler-policy-name = "${local.cluster_name}-cluster-autoscaler-oidc-policy"
  chartmuseum-role-name =  "${local.cluster_name}-chartmuseum-oidc"
  chartmuseum-policy-name = "${local.cluster_name}-chartmuseum-oidc-policy"
  fluent-bit-role-name =  "${local.cluster_name}-fluent-bit-oidc"
  fluent-bit-policy-name = "${local.cluster_name}-fluent-bit-oidc-policy"
  external-secrets-role-name =  "${local.cluster_name}-external-secrets-oidc"
  external-secrets-policy-name = "${local.cluster_name}-external-secrets-oidc-policy"
}

######################
# CLUSTER AUTOSCALER #
######################
data "template_file" "cluster-autoscaler-eks-role" {
  template = file("${path.module}/roles/cluster-autoscaler-role.json")

  vars = {
    eks_cluster_oidc_arn = local.eks_cluster_oidc_issuer_arn
    account_id = data.aws_caller_identity.current.account_id
  }
}

resource "aws_iam_role" "cluster-autoscaler-role-eks" {
  name                  = local.cluster-autoscaler-role-name
  assume_role_policy    = data.template_file.cluster-autoscaler-eks-role.rendered
  force_detach_policies = true

  tags                  = local.common_tags
}

data "template_file" "cluster-autoscaler-eks-policy" {
  template = file("${path.module}/policies/cluster-autoscaler-policy.json")
}

resource "aws_iam_policy" "cluster-autoscaler-eks" {
  name   = local.cluster-autoscaler-policy-name
  policy = data.template_file.cluster-autoscaler-eks-policy.rendered
}

resource "aws_iam_role_policy_attachment" "cluster-autoscaler-eks-attachment" {
  role       = aws_iam_role.cluster-autoscaler-role-eks.name
  policy_arn = aws_iam_policy.cluster-autoscaler-eks.arn
}

####################
# EXTERNAL SECRETS #
####################
data "template_file" "external-secrets-eks-role" {
  template = file("${path.module}/roles/external-secrets-role.json")

  vars = {
    eks_cluster_oidc_arn = local.eks_cluster_oidc_issuer_arn
    account_id = data.aws_caller_identity.current.account_id
  }
}

resource "aws_iam_role" "external-secrets-role-eks" {
  name                  = local.external-secrets-role-name
  assume_role_policy    = data.template_file.external-secrets-eks-role.rendered
  force_detach_policies = true

  tags                  = local.common_tags
}

data "template_file" "external-secrets-eks-policy" {
  template = file("${path.module}/policies/external-secrets-policy.json")

  vars = {
    account_id = data.aws_caller_identity.current.account_id
  }
}

resource "aws_iam_policy" "external-secrets-eks" {
  name   = local.external-secrets-policy-name
  policy = data.template_file.external-secrets-eks-policy.rendered
}

resource "aws_iam_role_policy_attachment" "external-secrets-eks-attachment" {
  role       = aws_iam_role.external-secrets-role-eks.name
  policy_arn = aws_iam_policy.external-secrets-eks.arn
}

resource "aws_ssm_parameter" "external-secrets-eks-parameter" {
  name        = "/automation-engine/${substr(var.CURRENT_ENVIRONMENT, 0, 3)}/external-secrets/iam-role-arn"
  description = "The ARN of the AWS IAM role necesary to manage parameter store and secret manager"
  type        = "SecureString"
  value       = aws_iam_role.external-secrets-role-eks.arn

  tags = merge(local.common_tags, {
    name = "external-secrets-iam-role-arn"
  })
}


######################
#    CHARTMUSEUM     #
######################
data "template_file" "chartmuseum-eks-role" {
  count    = var.CURRENT_ENVIRONMENT == "production" ? 1 : 0
  template = file("${path.module}/roles/chartmuseum-role.json")

  vars = {
    eks_cluster_oidc_arn = local.eks_cluster_oidc_issuer_arn
    account_id = data.aws_caller_identity.current.account_id
  }
}

resource "aws_iam_role" "chartmuseum-role-eks" {
  count                 = var.CURRENT_ENVIRONMENT == "production" ? 1 : 0
  name                  = local.chartmuseum-role-name
  assume_role_policy    = data.template_file.chartmuseum-eks-role[0].rendered
  force_detach_policies = true

  tags                  = local.common_tags
}

data "template_file" "chartmuseum-eks-policy" {
  count    = var.CURRENT_ENVIRONMENT == "production" ? 1 : 0
  template = file("${path.module}/policies/chartmuseum-policy.json")
  
  vars = {
    bucket_chartmuseum = aws_s3_bucket.bucket_chartmuseum[0].id
  }
}

resource "aws_iam_policy" "chartmuseum-eks" {
  count    = var.CURRENT_ENVIRONMENT == "production" ? 1 : 0
  name   = local.chartmuseum-policy-name
  policy = data.template_file.chartmuseum-eks-policy[0].rendered
}

resource "aws_iam_role_policy_attachment" "chartmuseum-eks-attachment" {
  count      = var.CURRENT_ENVIRONMENT == "production" ? 1 : 0
  role       = aws_iam_role.chartmuseum-role-eks[0].name
  policy_arn = aws_iam_policy.chartmuseum-eks[0].arn
}

##############
# FLUENT-BIT #
##############
data "template_file" "fluent-bit-eks-role" {
  count    = var.ENABLE_FLUENT_BIT ? 1 : 0
  template = file("${path.module}/roles/fluent-bit-role.json")

  vars = {
    eks_cluster_oidc_arn = local.eks_cluster_oidc_issuer_arn
    account_id = data.aws_caller_identity.current.account_id
  }
}

resource "aws_iam_role" "fluent-bit-role-eks" {
  count                 = var.ENABLE_FLUENT_BIT ? 1 : 0
  name                  = local.fluent-bit-role-name
  assume_role_policy    = data.template_file.fluent-bit-eks-role[0].rendered
  force_detach_policies = true

  tags                  = local.common_tags
}

data "template_file" "fluent-bit-eks-policy" {
  count    = var.ENABLE_FLUENT_BIT ? 1 : 0
  template = file("${path.module}/policies/fluent-bit-policy.json")
}

resource "aws_iam_policy" "fluent-bit-eks" {
  count  = var.ENABLE_FLUENT_BIT ? 1 : 0
  name   = local.fluent-bit-policy-name
  policy = data.template_file.fluent-bit-eks-policy[0].rendered
}

resource "aws_iam_role_policy_attachment" "fluent-bit-eks-attachment" {
  count      = var.ENABLE_FLUENT_BIT ? 1 : 0
  role       = aws_iam_role.fluent-bit-role-eks[0].name
  policy_arn = aws_iam_policy.fluent-bit-eks[0].arn
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
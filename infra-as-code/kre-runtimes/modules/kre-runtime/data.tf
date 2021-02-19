# Data from EKS cluster module
data "aws_eks_cluster" "cluster" {
  name = local.eks_cluster_name
}

data "aws_eks_cluster_auth" "cluster" {
  name = local.eks_cluster_name
}

# mettel-automation hosted zone info
data "aws_route53_zone" "mettel_automation" {
  name         = "mettel-automation.net."
  private_zone = false
}

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

## Data from VPC
data "aws_vpc" "mettel-automation-vpc" {
  filter {
    name   = "tag:Name"
    values = ["mettel-automation-vpc-${var.CURRENT_ENVIRONMENT}"] # insert values here
  }
}

data "aws_subnet_ids" "mettel-automation-private-subnets" {
  vpc_id = data.aws_vpc.mettel-automation-vpc.id

  filter {
    name   = "tag:Name"
    values = [
      "mettel-automation-private-subnet-1a-${var.CURRENT_ENVIRONMENT}",
      "mettel-automation-private-subnet-1b-${var.CURRENT_ENVIRONMENT}"
    ]
  }

  filter {
    name = "tag:Project"
    values = [
      var.common_info.project
    ]
  }

  filter {
    name = "tag:Type"
    values = [
      "Private"
    ]
  }

  filter {
    name = "tag:Environment"
    values = [
      var.CURRENT_ENVIRONMENT
    ]
  }
}

# Data from EKS Cluster Workers SG
data "aws_security_group" "eks_nodes_security_group" {
  filter {
    name   = "tag:Environment"
    values = [
      var.CURRENT_ENVIRONMENT
    ]
  }
  filter {
    name = "tag:Name"
    values = [
      local.eks_nodes_security_tag_name_value
    ]
  }
  filter {
    name = local.eks_cluster_tag_key
    values = [
      local.eks_cluster_tag_value
    ]
  }

  depends_on = [
    module.mettel-automation-eks-cluster
  ]
}

# Data from ELB created by ingress-nginx controller in EKS cluster
data "aws_security_group" "elb_ingress_nginx_eks_security_group" {
  filter {
    name = "group-name"
    values = [
      local.ingress_nginx_elb_sg_name
    ]
  }
  filter {
    name = local.eks_cluster_tag_key
    values = [
      local.eks_cluster_tag_value
    ]
  }

  depends_on = [
    module.mettel-automation-eks-cluster,
    helm_release.ingress-nginx
  ]
}

data "aws_s3_bucket" "bucket_logs" {
  bucket = "mettel-automation-logs"
}

data "aws_route53_zone" "mettel_automation" {
  name         = "mettel-automation.net."
  private_zone = false
}

# Data from ACM
data "aws_acm_certificate" "mettel_automation_certificate" {
  domain      = "*.mettel-automation.net"
  types       = ["AMAZON_ISSUED"]
  most_recent = true
}

# Data from EKS cluster module
data "aws_eks_cluster" "cluster" {
  name = module.mettel-automation-eks-cluster.cluster_id
}

data "aws_eks_cluster_auth" "cluster" {
  name = module.mettel-automation-eks-cluster.cluster_id
}
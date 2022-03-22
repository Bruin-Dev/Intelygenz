data "aws_caller_identity" "current" {}

# Data from other tfstate
# AWS Network Resources tfstate
data "terraform_remote_state" "tfstate-network-resources" {
  backend = "s3"
  config = {
    bucket = "automation-infrastructure"
    region = "us-east-1"
    key = "terraform-${terraform.workspace}-network-resources.tfstate"
  }
}

# AWS S3 Bucket for EKS tfstate
data "terraform_remote_state" "tfstate-s3-bucket-eks" {
  backend = "s3"
  config = {
    bucket = "automation-infrastructure"
    region = "us-east-1"
    key = "env:/${terraform.workspace}/mettel-automation-eks-kre-bucket.tfstate"
  }
}

data "aws_ami" "eks_worker_ami_name_filter" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amazon-eks-node-${local.k8s_version}-*"]
  }
}

# Data from EKS cluster module
data "aws_eks_cluster" "cluster" {
  name = module.mettel-automation-eks-cluster.cluster_id
}

data "aws_eks_cluster_auth" "cluster" {
  name = module.mettel-automation-eks-cluster.cluster_id
}

# mettel-automation hosted zone info
data "aws_route53_zone" "mettel_automation" {
  name         = "mettel-automation.net."
  private_zone = false
}

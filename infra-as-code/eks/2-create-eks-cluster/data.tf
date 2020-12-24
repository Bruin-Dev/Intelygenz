data "aws_vpc" "mettel-automation-vpc" {
  filter {
    name   = "tag:Name"
    values = ["mettel-automation-vpc-${var.CURRENT_ENVIRONMENT}"] # insert values here
  }
}

data "aws_subnet_ids" "mettel-automation-public-subnets" {
  vpc_id = data.aws_vpc.mettel-automation-vpc.id

  filter {
    name   = "tag:Name"
    values = [
      "mettel-automation-public-subnet-1a-${var.CURRENT_ENVIRONMENT}",
      "mettel-automation-public-subnet-1b-${var.CURRENT_ENVIRONMENT}"
    ]
  }
}

# Data from EKS cluster module
data "aws_eks_cluster" "cluster" {
  name = module.mettel-automation-eks-cluster.cluster_id
}

data "aws_eks_cluster_auth" "cluster" {
  name = module.mettel-automation-eks-cluster.cluster_id
}
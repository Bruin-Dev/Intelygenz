data "aws_vpc" "mettel-automation-vpc" {
  filter {
    name   = "tag:Name"
    values = ["mettel-automation-vpc-${var.CURRENT_ENVIRONMENT}"] # insert values here
  }
}

data "aws_subnet_ids" "mettel-automation-private-subnets" {
  vpc_id = data.aws_vpc.mettel-automation-vpc.id

  filter {
    name = "tag:Name"
    values = [
      "mettel-automation-private-subnet-1a-${var.CURRENT_ENVIRONMENT}",
      "mettel-automation-private-subnet-1b-${var.CURRENT_ENVIRONMENT}"
    ]
  }
}

data "aws_route53_zone" "mettel-automation-private-zone" {
  name         = local.automation-private-zone-Name
  private_zone = true
}

data "aws_security_group" "workers_security_group_eks" {
  filter {
    name = "tag:Name"
    values = [
      local.eks_workers_security_group_name
    ]
  }
}

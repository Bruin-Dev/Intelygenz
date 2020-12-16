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

data "aws_subnet_ids" "mettel-automation-private-subnets" {
  vpc_id = data.aws_vpc.mettel-automation-vpc.id

  filter {
    name   = "tag:Name"
    values = [
      "mettel-automation-private-subnet-1a-${var.CURRENT_ENVIRONMENT}",
      "mettel-automation-private-subnet-1b-${var.CURRENT_ENVIRONMENT}"
    ]
  }
}

data "aws_subnet" "mettel-automation-private-subnet-1a" {
  filter {
    name   = "tag:Name"
    values = ["mettel-automation-private-subnet-1a-${var.CURRENT_ENVIRONMENT}"]
  }
}

data "aws_subnet" "mettel-automation-private-subnet-1b" {
  filter {
    name   = "tag:Name"
    values = ["mettel-automation-private-subnet-1b-${var.CURRENT_ENVIRONMENT}"]
  }
}
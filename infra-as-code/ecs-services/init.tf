terraform {
  backend "s3" {
    bucket = "automation-infrastructure"
    region = "us-east-1"
    key = "terraform-ecs-services-resources.tfstate"
  }
}

provider "aws" {
  region = "us-east-1"
}


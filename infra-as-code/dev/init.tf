terraform {
  backend "s3" {
    bucket = "automation-infrastructure"
    region = "us-east-1"
    key = "terraform-${var.ENVIRONMENT}-dev-tests-network-resources.tfstate"
  }
}

provider "aws" {
  region = "us-east-1"
}

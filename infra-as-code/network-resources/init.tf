terraform {
  backend "s3" {
    bucket = "automation-infrastructure"
    region = "us-east-1"
    key = "terraform-tests-${var.CURRENT_ENVIRONMENT}-network-resources.tfstate"
  }
}

provider "aws" {
  region = "us-east-1"
}
terraform {
  backend "s3" {
    bucket          = "automation-infrastructure"
    region          = "us-east-1"
    key             = "terraform-dev-network-resources.tfstate"
    dynamodb_table  = "terraform-dev-network-resources-terraform-state-lock"
  }
}

provider "aws" {
  region = "us-east-1"
  version = "=2.49.0"
}

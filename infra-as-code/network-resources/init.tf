terraform {
  backend "s3" {
    bucket          = "automation-infrastructure"
    region          = "us-east-1"
    key             = "terraform-${TF_VAR_CURRENT_ENVIRONMENT}-network-resources.tfstate"
    dynamodb_table  = "terraform-${TF_VAR_CURRENT_ENVIRONMENT}-network-resources-terraform-state-lock"
  }
}

provider "aws" {
  region = "us-east-1"
  version = "=2.49.0"
}

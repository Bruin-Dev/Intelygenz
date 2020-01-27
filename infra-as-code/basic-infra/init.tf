terraform {
  backend "s3" {
    bucket = "automation-infrastructure"
    key = "terraform-automation-basic-infra.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = "us-east-1"
  version = "=2.46.0"
}

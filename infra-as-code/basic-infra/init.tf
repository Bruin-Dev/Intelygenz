terraform {
  backend "s3" {
    bucket = "automation-infrastructure"
    key = "terraform-automation-basic-infra-dev.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = "us-east-1"
}

variable "environment" {
  default = "automation-dev"
}
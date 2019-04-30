terraform {
  backend "s3" {
    bucket = "automation-infrastructure"
    key = "terraform-automation-dev.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = "us-east-1"
}

variable "environment" {
  default = "automation-dev"
}

variable "subdomain" {
  default = "automation-pro"
}

variable "build_number" {}

//variable "AWS_ACCESS_KEY_ID" {}
//variable "AWS_SECRET_ACCESS_KEY" {}

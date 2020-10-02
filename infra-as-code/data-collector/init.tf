terraform {
  backend "s3" {
    bucket = "automation-infrastructure"
    region = "us-east-1"
    key = "terraform-${TF_VAR_ENVIRONMENT}-data-collector.tfstate"
  }
}

provider "aws" {
  region = "us-east-1"
  version = "=3.9.0"
  max_retries = 25
}

provider "null" {
  version = "= 2.1"
}

provider "template" {
  version = "= 2.1"
}

provider "external" {
  version = "= 1.2"
}
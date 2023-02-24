# Global Terraform config with providers

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "= 3.70.0"
    }
    template = {
      source  = "hashicorp/template"
      version = "= 2.2.0"
    }
  }
  required_version = ">= 1.2, < 2.0"
}

# AWS provider config
provider "aws" {
  region      = "us-east-1"
  max_retries = 25
}
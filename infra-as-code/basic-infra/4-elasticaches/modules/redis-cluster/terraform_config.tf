# Global Terraform config with providers

terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "=3.47.0"
    }
  }
  required_version = "= 1.0.1"
}

# AWS provider config
provider "aws" {
  region = "us-east-1"
  max_retries = 25
}
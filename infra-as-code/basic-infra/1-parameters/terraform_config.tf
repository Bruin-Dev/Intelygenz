# Global Terraform config with providers
terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "~> 4.8.0"
    }
  }
  required_version = ">= 1.2, < 2.0"
}

# AWS provider config
provider "aws" {
  region      = local.region
  max_retries = 25
}

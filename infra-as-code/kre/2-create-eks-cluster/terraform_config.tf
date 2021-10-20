# Global Terraform config with providers
terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "= 3.47.0"
    }
    local = {
      source = "hashicorp/local"
      version = "= 2.1.0"
    }
    null = {
      source = "hashicorp/null"
      version = "= 2.1.0"
    }
    template = {
      source = "hashicorp/template"
      version = "= 2.1.0"
    }
    tls = {
      source = "hashicorp/tls"
      version = "= 2.2.0"
    }
    kubernetes = {
      source = "hashicorp/kubernetes"
      version = "= 2.0.1"
    }
    helm = {
      source = "hashicorp/helm"
      version = "= 1.3.2"
    }
  }
  required_version = ">= 1.0.1, < 1.1"
}
# AWS provider config
provider "aws" {
  region      = "us-east-1"
  max_retries = 25
}
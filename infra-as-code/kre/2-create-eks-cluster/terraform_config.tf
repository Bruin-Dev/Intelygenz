# Global Terraform config with providers
terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "= 4.6.0"
    }
    local = {
      source = "hashicorp/local"
      version = "= 2.2.2"
    }
    null = {
      source = "hashicorp/null"
      version = "= 3.1.1"
    }
    template = {
      source = "hashicorp/template"
      version = "= 2.2.0"
    }
    tls = {
      source = "hashicorp/tls"
      version = "= 3.1.0"
    }
    kubernetes = {
      source = "hashicorp/kubernetes"
      version = "= 2.9.0"
    }
    helm = {
      source = "hashicorp/helm"
      version = "= 2.4.1"
    }
    kubectl = {
      source = "gavinbunney/kubectl"
      version = ">=1.13.1"
    }
    http = {
      source  = "terraform-aws-modules/http"
      version = "2.4.1"
   }
  }
  required_version = ">= 1.1, < 1.2"
}
# AWS provider config
provider "aws" {
  region      = "us-east-1"
  max_retries = 25
}
# Global Terraform config with providers

terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "= 3.26.0"
    }
    external = {
      source = "hashicorp/external"
      version = "= 1.2.0"
    }
    local = {
      source = "hashicorp/local"
      version = "= 1.4.0"
    }
    null = {
      source = "hashicorp/null"
      version = "= 2.1.0"
    }
    random = {
      source = "hashicorp/random"
      version = "= 2.3.0"
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
  required_version = "= 0.14.4"
}

# AWS provider config
provider "aws" {
  region      = "us-east-1"
  max_retries = 25
}
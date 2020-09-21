# Global Terraform config
## AWS provider
provider "aws" {
  region = "us-east-1"
  version = "=3.4.0"
  max_retries = 25
}

## external provider
provider "external" {
  version = "= 1.2.0"
}

## local provider
provider "local" {
  version = "= 1.4.0"
}

## null provider
provider "null" {
  version = "= 2.1.0"
}

## random provider
provider "random" {
  version = "= 2.3.0"
}

## template provider
provider "template" {
  version = "= 2.1.0"
}

## tls provider
provider "tls" {
  version = "= 2.2.0"
}
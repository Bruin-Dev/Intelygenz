terraform {
  backend "s3" {
    bucket = "mettel-automation-pro"
    key = "terraform-mettel-automation-pro.tfstate"
    region = "us-east-2"
  }
}

provider "aws" {
  region = "us-east-1"
}

variable "environment" {
  default = "mettel-automation-pro"
}

variable "subdomain" {
  default = "mettel-automation-pro"
}

variable "build_number" {}

variable "AWS_ACCESS_KEY_ID" {}
variable "AWS_SECRET_ACCESS_KEY" {}
variable "NATS_SERVER1" {}
variable "NATS_CLUSTER_NAME" {}
variable "VELOCLOUD_CREDENTIALS" {}
variable "VELOCLOUD_VERIFY_SSL" {}
variable "SLACK_URL" {}

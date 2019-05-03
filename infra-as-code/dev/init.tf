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

variable "domain" {
  default = "mettel-automation.net"
}

variable "subdomain" {
  default = "dev"
}

variable "build_number" {}


variable "PYTHONUNBUFFERED" {
  default = 1
}

variable "NATS_SERVER1" {
  default = "nats://nats-streaming:4222"
}

variable "NATS_CLUSTER_NAME" {
  default = "automation-engine-nats"
}

variable "VELOCLOUD_CREDENTIALS_PRO" {}

variable "VELOCLOUD_VERIFY_SSL" {}

//variable "AWS_ACCESS_KEY_ID" {}
//variable "AWS_SECRET_ACCESS_KEY" {}

variable "cdir_base" {
  default = "10.1.0.0"
}

variable "cdir_public_1" {
  default = "10.1.1.0"
}

variable "cdir_public_2" {
  default = "10.1.2.0"
}

variable "cdir_private_1" {
  default = "10.1.11.0"
}

variable "cdir_private_2" {
  default = "10.1.12.0"
}

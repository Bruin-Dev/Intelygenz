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

variable "BUILD_NUMBER" {}


variable "PYTHONUNBUFFERED" {
  default = 1
}

variable "EMAIL_ACC_PWD" {}


variable "NATS_CLUSTER_NAME" {
  default = "automation-engine-nats"
}

variable "MONITORING_SECONDS" {
  default = "600"
}

variable "VELOCLOUD_CREDENTIALS" {}

variable "VELOCLOUD_VERIFY_SSL" {
  default = "yes"
}

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

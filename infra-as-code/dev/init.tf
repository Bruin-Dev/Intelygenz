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

variable "subdomain" {
  default = "automation-dev"
}

variable "build_number" {}

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

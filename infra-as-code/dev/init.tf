terraform {
  backend "s3" {
    bucket = "automation-infrastructure"
    region = "us-east-1"
    key = "terraform-${TF_VAR_ENVIRONMENT}.tfstate"
  }
}

provider "aws" {
  region = "us-east-1"
}

variable "ENVIRONMENT" {}

variable "domain" {
  default = "mettel-automation.net"
}

variable "SUBDOMAIN" {}

variable "BUILD_NUMBER" {
  default = ""
}

variable "NATS_MODULE_VERSION" {
  default = "latest"
}

variable "LAST_CONTACT_RECIPIENT" {
  default = ""
}

variable "PYTHONUNBUFFERED" {
  default = 1
}

variable "EMAIL_ACC_PWD" {
  default = ""
}

variable "NATS_CLUSTER_NAME" {
  default = "automation-engine-nats"
}

variable "MONITORING_SECONDS" {
  default = "600"
}

variable "VELOCLOUD_CREDENTIALS" {
  default = ""
}

variable "VELOCLOUD_VERIFY_SSL" {
  default = "yes"
}

variable "BRUIN_CLIENT_ID" {
  default = ""
}

variable "BRUIN_CLIENT_SECRET" {
  default = ""
}

variable "BRUIN_LOGIN_URL" {
  default = ""
}

variable "BRUIN_BASE_URL" {
  default = ""
}
variable "CURRENT_ENVIRONMENT" {
  default = "dev"
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

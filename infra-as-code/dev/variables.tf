variable "ENVIRONMENT" {
}

variable "domain" {
  default = "mettel-automation.net"
}

variable "SUBDOMAIN" {
}

variable "BUILD_NUMBER" {
  default = ""
}

variable "NATS_MODULE_VERSION" {
  default = "latest"
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

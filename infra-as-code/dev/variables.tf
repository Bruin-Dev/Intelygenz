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

variable "cidr_base" {
  type = "map"
  default = {
    "production"  = "10.1.0.0/16"
    "dev"         = "10.2.0.0/16"
  }
}

variable "CURRENT_ENVIRONMENT" {
  default = "dev"
  description = "Name of the environment to identify the network resources to be used"
  type = "string"
}
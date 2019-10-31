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

variable "NATS_SERVER_SEED_CLUSTER_PORT" {
  default = 5222
  type = number
  description = "NATS edge server cluster port"
}

variable "NATS_SERVER_SEED_CLIENTS_PORT" {
  default = "4222"
  type = string
  description = "Port for clients in NATS seed node"
}

variable "NATS_SERVER_SEED_CLUSTER_MODE" {
  default = "s"
  type = string
  description = "NATS seed node cluster mode"
}
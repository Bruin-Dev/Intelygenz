variable "cidr_base" {
  type = "map"
  default = {
    "production"  = "10.1.0.0/16"
    "dev"         = "10.2.0.0/16"
  }
}

variable "cdir_public_1" {
  type = "map"
  default = {
    "production"  = "10.1.1.0/24"
    "dev"         = "10.2.1.0/24"
  }
}

variable "cdir_public_2" {
  type = "map"
  default = {
    "production"  = "10.1.2.0/24"
    "dev"         = "10.2.2.0/24"
  }
}

variable "cdir_private_1" {
  type = "map"
  default = {
    "production"  = "10.1.11.0/24"
    "dev"         = "10.2.11.0/24"
  }
}

variable "cdir_private_2" {
  type = "map"
  default = {
    "production"  = "10.1.12.0/24"
    "dev"         = "10.2.12.0/24"
  }
}

variable "CURRENT_ENVIRONMENT" {
  default = "dev"
  description = "Name of the environment to identify the network resources to be used"
  type = "string"
}

variable "EKS_CLUSTER_NAMES" {
  description = "Name of the EKS cluster to allow deploy its ELB in the public subnets"
  default = {
    "dev" = ["mettel-automation-kre-dev", "mettel-automation-dev"]
    "production" = ["mettel-automation-kre", "mettel-automation"]
  }
}

variable "EKS_KRE_BASE_NAME" {
  type = string
  default = "mettel-automation-kre"
  description = "aa"
}

variable "EKS_PROJECT_BASE_NAME" {
  type = string
  default = "mettel-automation"
  description = "aa"
}
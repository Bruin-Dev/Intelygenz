variable "cidr_base" {
  description = "CIDR base for the environment"
  type = "map"
  default = {
    "production"  = "10.1.0.0/16"
    "dev"         = "172.31.84.0/22"
  }
}

variable "cdir_public_1" {
  description = "CIDR base for public subnet 1"
  type = "map"
  default = {
    "production"  = "10.1.1.0/24"
    "dev"         = "172.31.84.0/24"
  }
}

variable "cdir_public_2" {
  description = "CIDR base for public subnet 2"
  type = "map"
  default = {
    "production"  = "10.1.2.0/24"
    "dev"         = "172.31.85.0/24"
  }
}

variable "cdir_private_1" {
  description = "CIDR base for private subnet 1"
  type = "map"
  default = {
    "production"  = "10.1.11.0/24"
    "dev"         = "172.31.86.0/24"
  }
}

variable "cdir_private_2" {
  description = "CIDR base for private subnet 2"
  type = "map"
  default = {
    "production"  = "10.1.12.0/24"
    "dev"         = "172.31.87.0/24"
  }
}

# Global Tags
## kre infrastructure for mettel-automation project
variable "common_info" {
  type = map(string)
  default = {
    project      = "mettel-automation"
    provisioning = "Terraform"
  }
}

# Current environment variable
variable "CURRENT_ENVIRONMENT" {
  default = "dev"
  description = "Name of the environment to identify common resources to be used"
  type = string
}

variable "EKS_CLUSTER_NAMES" {
  description = "Name of the EKS cluster to allow deploy its ELB in the public subnets"
  default = {
    "dev" = [
      "mettel-automation-kre-dev",
      "mettel-automation-dev"
    ]
    "production" = [
      "mettel-automation-kre",
      "mettel-automation"
    ]
  }
}

variable "EKS_KRE_BASE_NAME" {
  type = string
  default = "mettel-automation-kre"
  description = "Base name used for EKS cluster used to deploy kre component"
}

variable "EKS_PROJECT_BASE_NAME" {
  type = string
  default = "mettel-automation"
  description = "Base name used for EKS cluster used to deploy project components"
}
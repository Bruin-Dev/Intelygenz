variable "cidr_base" {
  description = "CIDR base for the environment"
  type = map
  default = {
    "production"  = "172.31.88.0/22"
    "dev"         = "172.31.84.0/22"
  }
}

variable "cdir_public_1" {
  description = "CIDR base for public subnet 1"
  type = map
  default = {
    "production"  = "172.31.88.0/24"
    "dev"         = "172.31.84.0/24"
  }
}

variable "cdir_public_2" {
  description = "CIDR base for public subnet 2"
  type = map
  default = {
    "production"  = "172.31.89.0/24"
    "dev"         = "172.31.85.0/24"
  }
}

variable "cdir_private_1" {
  description = "CIDR base for private subnet 1"
  type = map
  default = {
    "production"  = "172.31.90.0/24"
    "dev"         = "172.31.86.0/24"
  }
}

variable "cdir_private_2" {
  description = "CIDR base for private subnet 2"
  type = map
  default = {
    "production"  = "172.31.91.0/24"
    "dev"         = "172.31.87.0/24"
  }
}

# Current environment variable
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
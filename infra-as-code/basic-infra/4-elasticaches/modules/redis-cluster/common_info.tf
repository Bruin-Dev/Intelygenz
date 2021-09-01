# Global Tags
## mettel-automation project
variable "common_info" {
  type = map(string)
  default = {
    project      = "mettel-automation"
    provisioning = "Terraform"
  }
}

variable "ENVIRONMENT" {
  default = "test"
  description = "Name of the current environment"
}

variable "REDIS_CLUSTER_NAME" {
  default = "redis"
  description = "Name of redis cluster"
}

variable "REDIS_TYPE" {
  type = string
  default = "general"
  description = "Describe type of redis (general or specific_for_microservices)"
}

# Current environment variable
variable "CURRENT_ENVIRONMENT" {
  default = "dev"
  description = "Name of the environment to identify common resources to be used"
  type = string
}

# Redis variables
variable "redis_node_type" {
  description = "Redis node type instance in each environment"
  type = map(map(string))
  default = {
    "general" = {
      "production"  = "cache.m4.large"
      "dev"         = "cache.t2.micro"
    }
    "specific_for_microservices" = {
        "production" = "cache.t2.small"
        "dev"        = "cache.t2.micro"
    }
  }
}
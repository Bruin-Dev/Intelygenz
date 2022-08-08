# Global Tags
## kre infrastructure for mettel-automation project
variable "common_info" {
  type = map(string)
  default = {
    project      = "mettel-automation-kre"
    provisioning = "Terraform"
  }
}

# Current environment variable
variable "CURRENT_ENVIRONMENT" {
  default = "dev"
  description = "Name of the environment to identify common resources to be used"
  type = string
}

variable "HOSTED_ZONE_DOMAIN_NAME" {
  default = "mettel-automation.net"
  description = "Name of the common domain name used in the project"
}

variable "RUNTIME_NAME" {
  default     = ""
  description = "Name of the runtime to create in KRE"
}
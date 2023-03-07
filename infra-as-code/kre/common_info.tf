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
  default     = "dev"
  description = "Name of the environment to identify common resources to be used"
  type        = string
}

variable "AWS_SECRET_ACCESS_KEY" {
  default     = ""
  description = "AWS Secret Access Key credentials"
}
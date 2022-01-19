# Global Tags
## mettel-automation project
variable "common_info" {
  type = map(string)
  default = {
    project      = "mettel-automation"
    provisioning = "Terraform"
  }
}

variable "FEDERAL_ACCOUNT_ID" {
  default = "663771866250"
  description = "Account ID of Federal AWS account"
  type = string
}

# Current environment variable
variable "CURRENT_ENVIRONMENT" {
  default = "dev"
  description = "Name of the environment to identify common resources to be used"
  type = string

}

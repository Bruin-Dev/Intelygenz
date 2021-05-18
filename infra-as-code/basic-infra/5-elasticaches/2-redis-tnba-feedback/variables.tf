variable "CURRENT_ENVIRONMENT" {
  default = "dev"
  description = "Name of the environment to identify common resources to be used"
  type = string
}

variable "ENVIRONMENT" {
  default = "test"
  description = "Name of the current environment"
}
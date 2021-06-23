variable "CURRENT_ENVIRONMENT" {
  default     = "dev"
  description = "current environment"
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
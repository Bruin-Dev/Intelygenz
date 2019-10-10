variable "cdir_base" {
  default = "10.1.0.0/16"
}

variable "cdir_public_1" {
  default = "10.1.1.0/24"
}

variable "cdir_public_2" {
  default = "10.1.2.0/24"
}

variable "cdir_private_1" {
  default = "10.1.11.0/24"
}

variable "cdir_private_2" {
  default = "10.1.12.0/24"
}

variable "cidr_vars" {
  type = "map"
  dev = {
    "cdir_base"  = "10.1.0.0/16"
    "cdir_public_1" = "10.1.1.0/24"
    "cdir_public_2" = "10.1.2.0/24"
    "cdir_private_1" = "10.1.11.0/24"
    "cdir_private_2" = "10.1.12.0/24"
  }
  production = {
    "cdir_base"  = "10.2.0.0/16"
    "cdir_public_1" = "10.2.1.0/24"
    "cdir_public_2" = "10.2.2.0/24"
    "cdir_private_1" = "10.2.11.0/24"
    "cdir_private_2" = "10.2.12.0/24"
  }
}

variable "CURRENT_ENVIRONMENT" {
  default = "dev"
  description = "Name of the environment to identify the network resources to be used"
  type = "string"
}
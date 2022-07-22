locals {
  region = "us-east-1"
  env    = substr(var.CURRENT_ENVIRONMENT, 0, 3)
}

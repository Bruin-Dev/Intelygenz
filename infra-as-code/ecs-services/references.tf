data "terraform_remote_state" "tfstate-dev-resources" {
  backend = "s3"
  config = {
    bucket = "automation-infrastructure"
    region = "us-east-1"
    key = "terraform-${var.ENVIRONMENT}-dev-tests-network-resources.tfstate"
  }
}

data "terraform_remote_state" "tfstate-network-resources" {
  backend = "s3"
  config = {
    bucket = "automation-infrastructure"
    region = "us-east-1"
    key = "terraform-tests-${var.CURRENT_ENVIRONMENT}-network-resources.tfstate"
  }
}
data "terraform_remote_state" "tfstate-network-resources" {
  backend = "s3"
  config = {
    bucket = "automation-infrastructure"
    region = "us-east-1"
    key = "env:/network-resources-${var.CURRENT_ENVIRONMENT}/terraform-network-resources.tfstate"
  }
}
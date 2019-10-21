data "terraform_remote_state" "tfstate-network-resources" {
  backend = "s3"
  config = {
    bucket = "automation-infrastructure"
    region = "us-east-1"
    key = "env:/${var.env_network_resources}-shared/terraform-automation-shared-infra.tfstate"
  }
}
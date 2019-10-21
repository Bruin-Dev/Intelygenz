data "terraform_remote_state" "tfstate-network-resources" {
  backend = "s3"
  config = {
    bucket = "automation-infrastructure"
    region = "us-east-1"
    key = "env:/${var.env_network_resources}/terraform-network-resources.tfstate"
  }
}
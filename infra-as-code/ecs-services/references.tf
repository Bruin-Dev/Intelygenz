data "terraform_remote_state" "tfstate-dev-resources" {
  backend = "s3"
  config {
    bucket = "automation-infrastructure"
    region = "us-east-1"
    key = "terraform-${TF_VAR_ENVIRONMENT}-dev.tfstate"
  }
}
terraform {
  backend "s3" {
    bucket = "automation-infrastructure"
    key = "terraform-automation-ecr-repositories.tfstate"
    region = "us-east-1"
  }
}

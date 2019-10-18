terraform {
  backend "s3" {
    bucket = "automation-infrastructure"
    region = "us-east-1"
    key = "terraform-test-metrics-dashboard-alarms.tfstate"
  }
}

provider "aws" {
  region = "us-east-1"
}
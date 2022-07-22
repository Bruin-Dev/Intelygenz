# EKS Backend
terraform {
  backend "s3" {
    bucket = "automation-infrastructure"
    region = "us-east-1"
    key    = "mettel-automation-k8s-eks.tfstate"
  }
}
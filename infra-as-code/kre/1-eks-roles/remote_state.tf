# EKS Backend
terraform {
  backend "s3" {
    bucket          = "automation-infrastructure"
    region          = "us-east-1"
    key             = "mettel-automation-k8s-kre-roles.tfstate"
    dynamodb_table  = "mettel-automation-k8s-kre-roles-terraform-state-lock"
  }
}
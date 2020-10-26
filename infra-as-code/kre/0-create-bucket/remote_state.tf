# EKS Backend
terraform {
  backend "s3" {
    bucket          = "automation-infrastructure"
    region          = "us-east-1"
    key             = "mettel-automation-eks-kre-bucket.tfstate"
    dynamodb_table  = "mettel-automation-eks-kre-bucket-terraform-state-lock"
  }
}

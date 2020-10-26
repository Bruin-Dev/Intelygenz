# EKS Backend
terraform {
  backend "s3" {
    bucket          = "automation-infrastructure"
    region          = "us-east-1"
    key             = "mettel-automation-k8s-kre.tfstate"
    dynamodb_table  = "automation-engine-kre-eks-cluster-terraform-state-lock"
  }
}

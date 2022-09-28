# Redis forticloud-cache remote state
terraform {
  backend "s3" {
    bucket = "automation-infrastructure"
    region = "us-east-1"
    key    = "mettel-automation-redis-forticloud-cache.tfstate"
  }
}
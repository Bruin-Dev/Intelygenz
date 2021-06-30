# Redis email-tagger remote state
terraform {
  backend "s3" {
    bucket = "automation-infrastructure"
    region = "us-east-1"
    key    = "mettel-automation-redis-email-tagger.tfstate"
  }
}
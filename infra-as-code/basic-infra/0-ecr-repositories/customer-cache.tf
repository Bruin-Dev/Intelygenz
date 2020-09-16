resource "aws_ecr_repository" "customer-cache-repository" {
  name = "customer-cache"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "customer-cache"
  }
}
resource "aws_ecr_repository" "hawkeye-customer-cache-repository" {
  name = "hawkeye-customer-cache"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "hawkeye-customer-cache"
  }
}
resource "aws_ecr_repository" "hawkeye-bridge-repository" {
  name = "hawkeye-bridge"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "bruin-bridge"
  }
}
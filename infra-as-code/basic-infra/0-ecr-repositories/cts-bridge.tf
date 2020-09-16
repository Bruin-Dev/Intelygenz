resource "aws_ecr_repository" "cts-bridge-repository" {
  name = "cts-bridge"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "cts-bridge"
  }
}
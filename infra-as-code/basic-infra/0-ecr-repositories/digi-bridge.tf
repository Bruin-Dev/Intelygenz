resource "aws_ecr_repository" "digi-bridge-repository" {
  name = "digi-bridge"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "digi-bridge"
  }
}
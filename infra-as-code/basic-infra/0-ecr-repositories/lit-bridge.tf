resource "aws_ecr_repository" "lit-bridge-repository" {
  name = "lit-bridge"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "lit-bridge"
  }
}
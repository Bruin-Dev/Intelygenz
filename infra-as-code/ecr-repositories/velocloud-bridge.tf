resource "aws_ecr_repository" "velocloud-bridge-repository" {
  name = "velocloud-bridge"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "velocloud-bridge"
  }
}
resource "aws_ecr_repository" "t7-bridge-repository" {
  name = "t7-bridge"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "t7-bridge"
  }
}
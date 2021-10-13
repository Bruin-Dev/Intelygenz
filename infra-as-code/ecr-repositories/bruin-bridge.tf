resource "aws_ecr_repository" "bruin-bridge-repository" {
  name = "bruin-bridge"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "bruin-bridge"
  }
}
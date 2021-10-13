resource "aws_ecr_repository" "bouncing-detector-repository" {
  name = "bouncing-detector"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "bouncing-detector"
  }
}
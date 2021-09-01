resource "aws_ecr_repository" "tnba-monitor-repository" {
  name = "tnba-monitor"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "tnba-monitor"
  }
}
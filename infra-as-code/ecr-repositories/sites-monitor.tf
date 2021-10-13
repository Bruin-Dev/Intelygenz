resource "aws_ecr_repository" "sites-monitor-repository" {
  name = "sites-monitor"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "sites-monitor"
  }
}
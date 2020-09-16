resource "aws_ecr_repository" "service-affecting-monitor-repository" {
  name = "service-affecting-monitor"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "service-affecting-monitor"
  }
}
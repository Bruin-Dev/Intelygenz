resource "aws_ecr_repository" "repair-tickets-monitor-repository" {
  name = "repair-tickets-monitor"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "repair-tickets-monitor"
  }
}
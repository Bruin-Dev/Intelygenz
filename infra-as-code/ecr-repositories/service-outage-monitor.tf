resource "aws_ecr_repository" "service-outage-monitor-repository" {
  name = "service-outage-monitor"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "service-outage-monitor"
  }
}
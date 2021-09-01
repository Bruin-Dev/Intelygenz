resource "aws_ecr_repository" "intermapper-outage-monitor-repository" {
  name = "intermapper-outage-monitor"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "intermapper-outage-monitor"
  }
}
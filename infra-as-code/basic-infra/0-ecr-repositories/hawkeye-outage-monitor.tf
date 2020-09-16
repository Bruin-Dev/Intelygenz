resource "aws_ecr_repository" "hawkeye-outage-monitor-repository" {
  name = "hawkeye-outage-monitor"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "hawkeye-outage-monitor"
  }
}
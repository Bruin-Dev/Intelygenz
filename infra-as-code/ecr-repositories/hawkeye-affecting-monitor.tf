resource "aws_ecr_repository" "hawkeye-affecting-monitor-repository" {
  name = "hawkeye-affecting-monitor"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "hawkeye-affecting-monitor"
  }
}
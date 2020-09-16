resource "aws_ecr_repository" "service-dispatch-monitor-repository" {
  name = "service-dispatch-monitor"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "service-dispatch-monitor"
  }
}
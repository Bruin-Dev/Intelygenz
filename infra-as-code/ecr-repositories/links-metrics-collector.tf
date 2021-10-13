resource "aws_ecr_repository" "links-metrics-collector-repository" {
  name = "links-metrics-collector"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "links-metrics-collector"
  }
}
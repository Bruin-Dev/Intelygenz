resource "aws_ecr_repository" "links-metrics-api-repository" {
  name = "links-metrics-api"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "links-metrics-api"
  }
}
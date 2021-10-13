resource "aws_ecr_repository" "ticket-collector-repository" {
  name = "ticket-collector"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "ticket-collector"
  }
}
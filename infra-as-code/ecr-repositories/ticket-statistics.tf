resource "aws_ecr_repository" "ticket-statistics-repository" {
  name = "ticket-statistics"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "ticket-statistics"
  }
}
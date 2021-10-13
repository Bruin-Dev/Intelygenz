resource "aws_ecr_repository" "dispatch-portal-backend-repository" {
  name = "dispatch-portal-backend"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "dispatch-portal-backend"
  }
}
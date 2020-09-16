resource "aws_ecr_repository" "dispatch-portal-frontend-repository" {
  name = "dispatch-portal-frontend"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "dispatch-portal-frontend"
  }
}
resource "aws_ecr_repository" "eks_reloader" {
  name = "reloader"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "reloader"
  }
}

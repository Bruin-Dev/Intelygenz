resource "aws_ecr_repository" "notifier-repository" {
  name = "notifier"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "notifier"
  }
}
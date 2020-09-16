resource "aws_ecr_repository" "tnba-feedback-repository" {
  name = "tnba-feedback"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "tnba-feedback"
  }
}
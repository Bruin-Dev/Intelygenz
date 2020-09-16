resource "aws_ecr_repository" "last-contact-report-repository" {
  name = "last-contact-report"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "last-contact-report"
  }
}
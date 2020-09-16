resource "aws_ecr_repository" "lumin-billing-report-repository" {
  name = "lumin-billing-report"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "lumin-billing-report"
  }
}
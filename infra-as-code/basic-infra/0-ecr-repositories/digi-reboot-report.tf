resource "aws_ecr_repository" "digi-reboot-report-repository" {
  name = "digi-reboot-report"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "digi-reboot-report"
  }
}
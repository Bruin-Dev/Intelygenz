resource "aws_ecr_repository" "email-tagger-monitor-repository" {
  name = "email-tagger-monitor"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "email-tagger-monitor"
  }
}
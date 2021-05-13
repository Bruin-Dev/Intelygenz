resource "aws_ecr_repository" "email-tagger-kre-bridge-repository" {
  name = "email-tagger-kre-bridge"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "email-tagger-kre-bridge"
  }
}
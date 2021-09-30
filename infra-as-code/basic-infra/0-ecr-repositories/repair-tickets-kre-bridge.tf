resource "aws_ecr_repository" "repair-tickets-kre-bridge-repository" {
  name = "repair-tickets-kre-bridge"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "repair-tickets-kre-bridge"
  }
}
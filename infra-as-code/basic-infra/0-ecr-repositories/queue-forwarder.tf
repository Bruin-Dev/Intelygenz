
resource "aws_ecr_repository" "queue-forwarder" {
  name = "queue-forwarder"

  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "notifier"
  }
}
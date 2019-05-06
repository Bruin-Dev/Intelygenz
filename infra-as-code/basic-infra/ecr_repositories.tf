resource "aws_ecr_repository" "automation-nats-server" {
  name = "${var.environment}-nats-streaming-server"
}

resource "aws_ecr_repository" "automation-velocloud-overseer" {
  name = "${var.environment}-velocloud-overseer"
}

resource "aws_ecr_repository" "automation-velocloud-drone" {
  name = "${var.environment}-velocloud-drone"
}


resource "aws_ecr_repository" "automation-velocloud-notificator" {
  name = "${var.environment}-velocloud-notificator"
}

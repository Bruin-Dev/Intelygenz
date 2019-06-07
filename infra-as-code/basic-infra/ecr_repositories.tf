resource "aws_ecr_repository" "automation-nats-server" {
  name = "${var.environment}-nats-streaming-server"
}

resource "aws_ecr_repository" "automation-velocloud-orchestrator" {
  name = "${var.environment}-velocloud-orchestrator"
}

resource "aws_ecr_repository" "automation-velocloud-bridge" {
  name = "${var.environment}-velocloud-bridge"
}

resource "aws_ecr_repository" "automation-velocloud-notificator" {
  name = "${var.environment}-velocloud-notificator"
}

resource "aws_ecr_repository" "automation-metrics-prometheus" {
  name = "${var.environment}-metrics-dashboard/prometheus"
}

resource "aws_ecr_repository" "automation-metrics-grafana" {
  name = "${var.environment}-metrics-dashboard/grafana"
}

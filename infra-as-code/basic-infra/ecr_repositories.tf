resource "aws_ecr_repository" "automation-nats-server" {
  name = "automation-nats-streaming-server"
}

resource "aws_ecr_repository" "automation-velocloud-orchestrator" {
  name = "automation-velocloud-orchestrator"
}

resource "aws_ecr_repository" "automation-last-contact-report" {
  name = "automation-last-contact-report"
}

resource "aws_ecr_repository" "automation-service-affecting-monitor" {
  name = "automation-service-affecting-monitor"
}

resource "aws_ecr_repository" "automation-service-outage-monitor" {
  name = "automation-service-outage-monitor"
}

resource "aws_ecr_repository" "automation-service-outage-triage" {
  name = "automation-service-outage-triage"
}

resource "aws_ecr_repository" "automation-velocloud-bridge" {
  name = "automation-velocloud-bridge"
}

resource "aws_ecr_repository" "automation-bruin-bridge" {
  name = "automation-bruin-bridge"
}

resource "aws_ecr_repository" "automation-t7-bridge" {
  name = "automation-t7-bridge"
}

resource "aws_ecr_repository" "automation-notifier" {
  name = "automation-notifier"
}

resource "aws_ecr_repository" "automation-metrics-prometheus" {
  name = "automation-metrics-dashboard/prometheus"
}

resource "aws_ecr_repository" "automation-metrics-grafana" {
  name = "automation-metrics-dashboard/grafana"
}

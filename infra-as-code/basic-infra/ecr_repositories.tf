resource "aws_ecr_repository" "automation-nats-server" {
  name = "automation-nats-server-2"
}

resource "aws_ecr_repository" "automation-velocloud-orchestrator" {
  name = "automation-velocloud-orchestrator-2"
}

resource "aws_ecr_repository" "automation-last-contact-report" {
  name = "automation-last-contact-report-2"
}

resource "aws_ecr_repository" "automation-service-affecting-monitor" {
  name = "automation-service-affecting-monitor-2"
}

resource "aws_ecr_repository" "automation-service-outage-monitor" {
  name = "automation-service-outage-monitor-2"
}

resource "aws_ecr_repository" "automation-service-outage-triage" {
  name = "automation-service-outage-triage-2"
}

resource "aws_ecr_repository" "automation-velocloud-bridge" {
  name = "automation-velocloud-bridge-2"
}

resource "aws_ecr_repository" "automation-bruin-bridge" {
  name = "automation-bruin-bridge-2"
}

resource "aws_ecr_repository" "automation-t7-bridge" {
  name = "automation-t7-bridge-2"
}

resource "aws_ecr_repository" "automation-notifier" {
  name = "automation-notifier-2"
}

resource "aws_ecr_repository" "automation-metrics-prometheus" {
  name = "automation-metrics-dashboard/prometheus-2"
}

resource "aws_ecr_repository" "automation-metrics-grafana" {
  name = "automation-metrics-dashboard/grafana-2"
}

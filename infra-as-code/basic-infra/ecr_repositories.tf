resource "aws_ecr_repository" "automation-nats-server" {
  name = "automation-nats-server"
}

resource "aws_ecr_repository" "automation-dispatch-portal-backend" {
  name = "automation-dispatch-portal-backend"
}

resource "aws_ecr_repository" "automation-sites-monitor" {
  name = "automation-sites-monitor"
}

resource "aws_ecr_repository" "automation-last-contact-report" {
  name = "automation-last-contact-report"
}

resource "aws_ecr_repository" "automation-service-affecting-monitor" {
  name = "automation-service-affecting-monitor"
}

resource "aws_ecr_repository" "automation-service-dispatch-monitor" {
  name = "automation-service-dispatch-monitor"
}

resource "aws_ecr_repository" "automation-service-outage-monitor" {
  name = "automation-service-outage-monitor"
}

resource "aws_ecr_repository" "automation-velocloud-bridge" {
  name = "automation-velocloud-bridge"
}

resource "aws_ecr_repository" "automation-bruin-bridge" {
  name = "automation-bruin-bridge"
}

resource "aws_ecr_repository" "automation-lit-bridge" {
  name = "automation-lit-bridge"
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

resource "aws_ecr_repository" "automation-metrics-thanos" {
  name = "automation-metrics-dashboard/thanos"
}

resource "aws_ecr_repository" "automation-metrics-thanos-store-gateway" {
  name = "automation-metrics-dashboard/thanos-store-gateway"
}

resource "aws_ecr_repository" "automation-metrics-thanos-querier" {
  name = "automation-metrics-dashboard/thanos-querier"
}

resource "aws_ecr_repository" "automation-dispatch-portal-frontend-nextjs" {
  name = "automation-dispatch-portal-frontend"
}

resource "aws_ecr_repository" "automation-dispatch-portal-frontend-nginx" {
  name = "automation-dispatch-portal-frontend/nginx"
}

resource "aws_ecr_repository" "automation-tnba-feedback" {
  name = "automation-tnba-feedback"
}

resource "aws_ecr_repository" "automation-tnba-monitor" {
  name = "automation-tnba-monitor"
}

resource "aws_ecr_repository" "automation-cts-bridge" {
  name = "automation-cts-bridge"
}

resource "aws_ecr_repository" "automation-customer-cache" {
  name = "automation-customer-cache"
}

resource "aws_ecr_repository" "automation-lumin-billing-report" {
  name = "automation-lumin-billing-report"
}

resource "aws_ecr_repository" "automation-hawkeye-affecting-monitor" {
  name = "automation-hawkeye-affecting-monitor"
}

resource "aws_ecr_repository" "automation-hawkeye-bridge" {
  name = "automation-hawkeye-bridge"
}

resource "aws_ecr_repository" "automation-hawkeye-customer-cache" {
  name = "automation-hawkeye-customer-cache"
}

resource "aws_ecr_repository" "automation-hawkeye-outage-monitor" {
  name = "automation-hawkeye-outage-monitor"
}

resource "aws_ecr_repository" "automation-digi-bridge" {
  name = "automation-digi-bridge"
}

resource "aws_ecr_repository" "automation-email-tagger-monitor" {
  name = "automation-email-tagger-monitor"
}

resource "aws_ecr_repository" "automation-email-tagger-kre-bridge" {
  name = "automation-email-tagger-kre-bridge"
}

resource "aws_ecr_repository" "automation-intermapper-outage-monitor" {
  name = "automation-intermapper-outage-monitor"
}
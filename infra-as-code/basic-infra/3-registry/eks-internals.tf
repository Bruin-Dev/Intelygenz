resource "aws_ecr_repository" "eks_reloader" {
  name = "reloader"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "reloader"
  }
}

resource "aws_ecr_repository" "eks_external_dns" {
  name = "external-dns"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "external-dns"
  }
}

resource "aws_ecr_repository" "eks_external_secrets" {
  name = "external-secrets"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "external-secrets"
  }
}

resource "aws_ecr_repository" "eks_fluent_bit" {
  name = "fluent-bit"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "fluent-bit"
  }
}

resource "aws_ecr_repository" "eks_kyverno" {
  name = "kyverno"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "kyverno"
  }
}

resource "aws_ecr_repository" "eks_metrics_server" {
  name = "metrics-server"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "metrics-server"
  }
}

resource "aws_ecr_repository" "eks_ingress_nginx_controller" {
  name = "ingress-nginx-controller"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "ingress-nginx-controller"
  }
}

resource "aws_ecr_repository" "eks_cluster_autoscaler_aws" {
  name = "cluster-autoscaler-aws"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "cluster-autoscaler-aws"
  }
}

resource "aws_ecr_repository" "eks_nats" {
  name = "nats"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "nats"
  }
}

resource "aws_ecr_repository" "eks_prometheus-nats-exporter" {
  name = "prometheus-nats-exporter"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "prometheus-nats-exporter"
  }
}

resource "aws_ecr_repository" "eks_reloader" {
  name = "eks_reloader"
  tags = {
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
    Module       = "reloader"
  }
}

resource "aws_ecr_repository" "eks_external_dns" {
  name = "eks_external-dns"
  tags = {
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
    Module       = "external-dns"
  }
}

resource "aws_ecr_repository" "eks_external_secrets" {
  name = "eks_external-secrets"
  tags = {
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
    Module       = "external-secrets"
  }
}

resource "aws_ecr_repository" "eks_fluent_bit" {
  name = "eks_fluent-bit"
  tags = {
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
    Module       = "fluent-bit"
  }
}

resource "aws_ecr_repository" "eks_kyverno" {
  name = "eks_kyverno"
  tags = {
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
    Module       = "kyverno"
  }
}

resource "aws_ecr_repository" "eks_metrics_server" {
  name = "eks_metrics-server"
  tags = {
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
    Module       = "metrics-server"
  }
}

resource "aws_ecr_repository" "eks_ingress_nginx_controller" {
  name = "eks_ingress-nginx-controller"
  tags = {
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
    Module       = "ingress-nginx-controller"
  }
}

resource "aws_ecr_repository" "eks_cluster_autoscaler_aws" {
  name = "eks_cluster-autoscaler-aws"
  tags = {
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
    Module       = "cluster-autoscaler-aws"
  }
}

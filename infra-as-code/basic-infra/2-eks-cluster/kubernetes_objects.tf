resource "kubernetes_namespace" "prometheus" {
  metadata {
    name = "prometheus"
  }

  depends_on = [
    module.mettel-automation-eks-cluster
  ]
}

resource "kubernetes_secret" "grafana_auth" {
  metadata {
    name      = "auth-grafana"
    namespace = "prometheus"
  }

  data = {
    user     = var.GRAFANA_ADMIN_USER
    password = var.GRAFANA_ADMIN_PASSWORD
  }

  depends_on = [
    module.mettel-automation-eks-cluster,
    kubernetes_namespace.prometheus
  ]
}

locals {
  key_config_yaml = <<EOT
          key: |
            ${indent(12, var.COSIGN_PUBLIC_KEY)}
EOT
}

data "template_file" "yaml_kyverno_cluster_policy" {
  template = file("${path.module}/yamls/kyverno_cluster_policy.yaml")
  vars = {
    REPOSITORY_URL  = var.REPOSITORY_URL
    KEY_CONFIG_YAML = local.key_config_yaml
  }
}

resource "kubectl_manifest" "kyverno_cluster_policy" {
  yaml_body = data.template_file.yaml_kyverno_cluster_policy.rendered
  
  depends_on = [
    module.mettel-automation-eks-cluster,
    helm_release.descheduler,
    helm_release.external-secrets,
    helm_release.external-dns,
    helm_release.ingress-nginx,
    helm_release.metrics-server,
    helm_release.reloader,
    helm_release.kyverno,
  ]  
}
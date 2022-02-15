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

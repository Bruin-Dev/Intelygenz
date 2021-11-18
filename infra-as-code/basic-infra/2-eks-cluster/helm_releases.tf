resource "helm_release" "cluster-autoscaler" {
  name          = "cluster-autoscaler"

  repository    = "https://kubernetes.github.io/autoscaler"
  chart         = "cluster-autoscaler"

  version       = var.CLUSTER_AUTOSCALER_HELM_CHART_VERSION
  namespace     = "kube-system"
  force_update  = false
  wait          = true
  recreate_pods = false

  values = [
    file("helm/external-charts/cluster-autoscaler-values.yaml")
  ]

  set {
    name = "autoDiscovery.clusterName"
    value = module.mettel-automation-eks-cluster.cluster_id
    type  = "string"
  }

  set {
    name = "rbac.serviceAccount.annotations.\\eks\\.amazonaws\\.com/role-arn"
    value = aws_iam_role.cluster-autoscaler-role-eks.arn
    type  = "string"
  }

  depends_on = [
      aws_iam_role.cluster-autoscaler-role-eks,
      null_resource.associate-iam-oidc-provider,
      module.mettel-automation-eks-cluster,
      data.aws_eks_cluster_auth.cluster,
      data.aws_eks_cluster.cluster
   ]
}

resource "helm_release" "chartmuseum" {
  count         = var.CURRENT_ENVIRONMENT == "production" ? 1 : 0
  name          = "chartmuseum"

  repository    = "https://chartmuseum.github.io/charts"
  chart         = "chartmuseum"

  version       = var.CHARTMUSEUM_HELM_CHART_VERSION
  namespace     = "kube-system"
  force_update  = false
  wait          = true
  recreate_pods = false

  values = [
    file("helm/external-charts/chartmuseum-values.yaml")
  ]

  set {
    name = "env.open.STORAGE_AMAZON_BUCKET"
    value = aws_s3_bucket.bucket_chartmuseum[0].id
    type  = "string"
  }

  set {
    name = "env.open.STORAGE_AMAZON_REGION"
    value = aws_s3_bucket.bucket_chartmuseum[0].region
    type  = "string"
  }

  set {
    name = "env.secret.BASIC_AUTH_USER"
    value = var.CHARTMUSEUM_USER
    type  = "string"
  }

  set {
    name = "env.secret.BASIC_AUTH_PASS"
    value = var.CHARTMUSEUM_PASSWORD
    type  = "string"
  }

  set {
    name = "serviceAccount.annotations.\\eks\\.amazonaws\\.com/role-arn"
    value = aws_iam_role.chartmuseum-role-eks[0].arn
    type  = "string"
  }

  depends_on = [
      aws_s3_bucket.bucket_chartmuseum,
      aws_iam_role.chartmuseum-role-eks,
      null_resource.associate-iam-oidc-provider,
      module.mettel-automation-eks-cluster,
      data.aws_eks_cluster_auth.cluster,
      data.aws_eks_cluster.cluster
   ]
}

resource "helm_release" "external-dns" {
  name          = "external-dns"

  repository    = "https://charts.bitnami.com/bitnami"
  chart         = "external-dns"

  version       = var.EXTERNAL_DNS_HELM_CHART_VERSION
  namespace     = "kube-system"
  force_update  = false
  wait          = true
  recreate_pods = false

  values = [
    file("helm/external-charts/external-dns-values.yaml")
  ]

  set {
    name = "serviceAccount.annotations.\\eks\\.amazonaws\\.com/role-arn"
    value = aws_iam_role.external-dns-role-eks.arn
    type  = "string"
  }

  depends_on = [
      aws_iam_role.external-dns-role-eks,
      null_resource.associate-iam-oidc-provider,
      module.mettel-automation-eks-cluster,
      data.aws_eks_cluster_auth.cluster,
      data.aws_eks_cluster.cluster
   ]
}

resource "helm_release" "ingress-nginx" {
  name          = "ingress-nginx"

  repository    = "https://kubernetes.github.io/ingress-nginx"
  chart         = "ingress-nginx"

  version       = var.INGRESS_NGINX_HELM_CHART_VERSION
  namespace     = "kube-system"
  force_update  = false
  recreate_pods = false
  wait          = true

  values = [
    file("helm/external-charts/ingress-nginx-values.yaml")
  ]

  dynamic "set" {
    for_each = var.WHITELISTED_IPS
    content {
      name = join("", ["controller.service.loadBalancerSourceRanges[", set.key, "]"])
      value = set.value
    }
  }

  set {
    name = "controller.service.annotations.\\service\\.beta\\.kubernetes\\.io/aws-load-balancer-ssl-cert"
    value = data.aws_acm_certificate.mettel_automation_certificate.arn
  }

  depends_on = [
      module.mettel-automation-eks-cluster,
      aws_iam_role.external-dns-role-eks,
      null_resource.associate-iam-oidc-provider,
      data.aws_eks_cluster_auth.cluster,
   ]
}

resource "helm_release" "reloader" {
  name          = "reloader"

  repository    = "https://stakater.github.io/stakater-charts"
  chart         = "reloader"

  version       = var.RELOADER_CHART_VERSION
  namespace     = "default"
  force_update  = false
  recreate_pods = false
  wait          = true

  depends_on = [
      module.mettel-automation-eks-cluster,
      data.aws_eks_cluster_auth.cluster,
   ]
}
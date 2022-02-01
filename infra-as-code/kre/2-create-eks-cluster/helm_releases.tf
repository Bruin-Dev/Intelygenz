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

resource "helm_release" "cert-manager" {
  name              = "cert-manager"

  repository        = "https://charts.jetstack.io"
  chart             = "cert-manager"

  version           = var.CERT_MANAGER_HELM_CHART_VERSION
  namespace         = "cert-manager"
  force_update      = true
  wait              = true
  create_namespace  = true


  set {
    name = "installCRDs"
    value = true
  }

  depends_on = [
      module.mettel-automation-eks-cluster,
      data.aws_eks_cluster_auth.cluster,
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

  depends_on = [
      module.mettel-automation-eks-cluster,
      aws_iam_role.external-dns-role-eks,
      null_resource.associate-iam-oidc-provider,
      data.aws_eks_cluster_auth.cluster,
   ]
}

resource "helm_release" "hostpath-provisioner" {
  name          = "hostpath-provisioner"

  repository    = "https://charts.rimusz.net"
  chart         = "hostpath-provisioner"

  version       = var.HOSTPATH_HELM_CHART_VERSION
  namespace     = "kube-system"
  force_update  = false
  recreate_pods = false
  wait          = true

  values = [
    file("helm/external-charts/hostpath-provisioner.yaml")
  ]

  depends_on = [
      module.mettel-automation-eks-cluster,
      null_resource.associate-iam-oidc-provider,
      data.aws_eks_cluster_auth.cluster,
   ]
}

resource "helm_release" "local-path-provisioner" {
  name          = "local-path-provisioner"

  repository    = "https://ebrianne.github.io/helm-charts"
  chart         = "local-path-provisioner"

  version       = var.LOCAL_PATH_PROVISIONER_HELM_CHART_VERSION
  namespace     = "kube-system"
  force_update  = false
  recreate_pods = false
  wait          = true

  values = [
    file("helm/external-charts/local-path-provisioner.yaml")
  ]

  set {
    name = "nodePathMap[0].paths"
    value = "{/mnt/efs/${local.cluster_name}}"
    type  = "string"
  }

  depends_on = [
      module.mettel-automation-eks-cluster,
      null_resource.associate-iam-oidc-provider,
      data.aws_eks_cluster_auth.cluster,
   ]
}
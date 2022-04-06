####################################################
### EBS CSI (Container Storage Interface)
### to support gp3 ebs persistent volumens lifecycle
####################################################

resource "helm_release" "aws-ebs-csi-driver" {
  name          = "aws-ebs-csi-driver"

  repository    = "https://kubernetes-sigs.github.io/aws-ebs-csi-driver"
  chart         = "aws-ebs-csi-driver"

  version       = var.EBS_CSI_HELM_CHART_VERSION
  namespace     = "kube-system"
  force_update  = false
  wait          = true
  recreate_pods = false

  set {
    name  = "node.tolerateAllTaints"
    value = "true"
  }

  set {
    name  = "controller.serviceAccount.create"
    value = "true"
    type  = "string"
  }

  set {
    name = "controller.serviceAccount.annotations.\\eks\\.amazonaws\\.com/role-arn"
    value = aws_iam_role.aws-ebs-csi-driver-role-eks.arn
    type  = "string"
  }

  depends_on = [
      kubectl_manifest.aws_auth,
      aws_eks_addon.vpc_cni,
      aws_eks_addon.kube_proxy,
      aws_eks_addon.coredns,
      aws_iam_role.aws-ebs-csi-driver-role-eks,
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
      kubectl_manifest.aws_auth,
      aws_eks_addon.vpc_cni,
      helm_release.aws-ebs-csi-driver,
      aws_eks_addon.kube_proxy,
      aws_eks_addon.coredns,
      aws_iam_role.external-dns-role-eks,
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

  depends_on = [
      kubectl_manifest.aws_auth,
      aws_eks_addon.vpc_cni,
      helm_release.aws-ebs-csi-driver,
      aws_eks_addon.kube_proxy,
      aws_eks_addon.coredns,
      module.mettel-automation-eks-cluster,
      aws_iam_role.external-dns-role-eks,
      data.aws_eks_cluster_auth.cluster,
   ]
}

resource "helm_release" "metrics-server" {
  name          = "metrics-server"

  repository    = "https://kubernetes-sigs.github.io/metrics-server/"
  chart         = "metrics-server"

  version       = var.METRICS_SERVER_HELM_CHART_VERSION
  namespace     = "kube-system"
  force_update  = false
  recreate_pods = false
  wait          = true

  depends_on = [
      kubectl_manifest.aws_auth,
      aws_eks_addon.vpc_cni,
      helm_release.aws-ebs-csi-driver,
      aws_eks_addon.kube_proxy,
      aws_eks_addon.coredns,
      module.mettel-automation-eks-cluster,
      data.aws_eks_cluster_auth.cluster,
   ]
}


resource "helm_release" "descheduler" {
  name          = "descheduler"

  repository    = "https://kubernetes-sigs.github.io/descheduler/"
  chart         = "descheduler"

  version       = var.DESCHEDULER_HELM_CHART_VERSION
  namespace     = "kube-system"
  force_update  = false
  wait          = true
  recreate_pods = false

  values = [
    file("helm/external-charts/descheduler-values.yaml")
  ]

  depends_on = [
      kubectl_manifest.aws_auth,
      aws_eks_addon.vpc_cni,
      helm_release.aws-ebs-csi-driver,
      aws_eks_addon.kube_proxy,
      aws_eks_addon.coredns,
      module.mettel-automation-eks-cluster,
      data.aws_eks_cluster_auth.cluster,
   ]
}
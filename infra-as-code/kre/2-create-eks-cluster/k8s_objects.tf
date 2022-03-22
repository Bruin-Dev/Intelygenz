resource "kubernetes_storage_class" "gp3" {
  metadata {
    name = "gp3"
  }
  storage_provisioner  = "ebs.csi.aws.com"
  reclaim_policy       = "Delete"
  volume_binding_mode  = "WaitForFirstConsumer"
  parameters = {
    type = "gp3",
    encrypted = false
  }
  mount_options = ["debug"]

  depends_on = [
    module.mettel-automation-eks-cluster,
          helm_release.aws-ebs-csi-driver
  ]
}

module "cert_manager" {
  source                                 = "terraform-iaac/cert-manager/kubernetes"
  cluster_issuer_email                   = "mettel@intelygenz.com"
  cluster_issuer_name                    = "cert-manager-kre"
  cluster_issuer_private_key_secret_name = "cert-manager-private-key"

  additional_set = [
    {
        name  = "serviceAccount.annotations.\\eks\\.amazonaws\\.com/role-arn"
        value = aws_iam_role.cert-manager-role-eks.arn
        type  = "string"
    }
  ]

  solvers = [
    {
      dns01 = {
        route53 = {
          region  = local.aws_default_region
        }
      },
      selector = {
        dnsZones = [
          local.dnz_zone_email_tagger,
          local.dnz_zone_tnba,
          local.dnz_zone_rta
        ]
      }
    },
    {
      http01 = {
        ingress = {
          class = "nginx"
        }
      }
    }
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
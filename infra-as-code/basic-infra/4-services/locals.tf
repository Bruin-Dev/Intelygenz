locals {
  // EKS cluster local variables
  cluster_name                      = var.CURRENT_ENVIRONMENT == "dev" ? "${var.common_info.project}-${var.CURRENT_ENVIRONMENT}" : var.common_info.project
  logs_name                         = var.CURRENT_ENVIRONMENT == "dev" ? "DEV-${var.common_info.project}-${var.CURRENT_ENVIRONMENT}-logs" : "PRO-${var.common_info.project}-logs"
  logs_dns_name                     = var.CURRENT_ENVIRONMENT == "dev" ? "docs-dev.${data.aws_route53_zone.mettel_automation.name}" : "docs.${data.aws_route53_zone.mettel_automation.name}"
  k8s_version                       = "1.21"
  min_worker_nodes                  = var.CURRENT_ENVIRONMENT == "dev" ? 5 : 5
  max_worker_nodes                  = var.CURRENT_ENVIRONMENT == "dev" ? 10 : 10
  eks_worker_ami_name_filter        = "amazon-eks-node-${local.k8s_version}-*"
  eks_worker_ami_owner_id           = "amazon"
  eks_worker_root_volume_type       = "gp3"
  eks_cluster_tag_key               = "tag:kubernetes.io/cluster/${data.aws_eks_cluster.cluster.name}"
  eks_cluster_tag_value             = "owned"
  eks_nodes_security_tag_name_value = var.CURRENT_ENVIRONMENT == "dev" ? "${var.common_info.project}-${var.CURRENT_ENVIRONMENT}-eks_worker_sg" : "${var.common_info.project}-eks_worker_sg"

  // ingress nginx local vars
  ingress_nginx_elb_sg_name = "k8s-elb-*"

  // EKS cluster access key local variables
  ssh_key_name = var.CURRENT_ENVIRONMENT == "dev" ? "${var.common_info.project}-${var.CURRENT_ENVIRONMENT}-eks-key" : "${var.common_info.project}-eks-key"

  // S3 bucket
  bucket_eks_name           = var.CURRENT_ENVIRONMENT == "dev" ? "${var.common_info.project}-${var.CURRENT_ENVIRONMENT}-eks" : "${var.common_info.project}-eks"
  bucket_chartmuseum_name   = var.CURRENT_ENVIRONMENT == "dev" ? "${var.common_info.project}-${var.CURRENT_ENVIRONMENT}-chartmuseum" : "${var.common_info.project}-chartmuseum"
  short_current_environment = var.CURRENT_ENVIRONMENT == "dev" ? var.CURRENT_ENVIRONMENT : "pro"

  // common tags
  common_tags = {
    Environment  = terraform.workspace
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
  }
}

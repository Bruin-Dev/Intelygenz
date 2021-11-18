locals {
  // EKS cluster local variables
  cluster_name = var.CURRENT_ENVIRONMENT == "dev" ? "${var.common_info.project}-${var.CURRENT_ENVIRONMENT}" : var.common_info.project
  logs_name = var.CURRENT_ENVIRONMENT == "dev" ? "DEV-${var.common_info.project}-${var.CURRENT_ENVIRONMENT}-logs" : "PRO-${var.common_info.project}-logs"
  k8s_version = "1.18"
  worker_nodes_instance_type = "t3.large"
  min_worker_nodes = var.CURRENT_ENVIRONMENT == "dev" ? 4 : 4
  max_worker_nodes = var.CURRENT_ENVIRONMENT == "dev" ? 10 : 10
  eks_worker_ami_name_filter = "amazon-eks-node-${local.k8s_version}-*"
  eks_worker_ami_owner_id = "amazon"
  eks_worker_root_volume_type = "gp2"
  eks_cluster_tag_key = "tag:kubernetes.io/cluster/${data.aws_eks_cluster.cluster.name}"
  eks_cluster_tag_value = "owned"
  eks_nodes_security_tag_name_value = var.CURRENT_ENVIRONMENT == "dev" ? "${var.common_info.project}-${var.CURRENT_ENVIRONMENT}-eks_worker_sg" : "${var.common_info.project}-eks_worker_sg"

  // ingress nginx local vars
  ingress_nginx_elb_sg_name = "k8s-elb-*"

  // EKS cluster access key local variables
  ssh_key_name = var.CURRENT_ENVIRONMENT == "dev" ? "${var.common_info.project}-${var.CURRENT_ENVIRONMENT}-eks-key" : "${var.common_info.project}-eks-key"

  // S3 bucket with EKS cluster info local variables
  bucket_name = var.CURRENT_ENVIRONMENT == "dev" ? "${var.common_info.project}-${var.CURRENT_ENVIRONMENT}-eks" : "${var.common_info.project}-eks"
  // S3 bucket for chartmuseum repository
  chartmuseum_bucket_name = var.CURRENT_ENVIRONMENT == "dev" ? "${var.common_info.project}-${var.CURRENT_ENVIRONMENT}-chartmuseum" : "${var.common_info.project}-chartmuseum"
  // common tags
  common_tags = {
    Environment  = terraform.workspace
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
  }
}
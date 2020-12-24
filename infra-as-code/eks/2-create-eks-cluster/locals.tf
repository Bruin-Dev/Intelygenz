locals {
  // EKS cluster local variables
  cluster_name = var.CURRENT_ENVIRONMENT == "dev" ? "${var.common_info.project}-${var.CURRENT_ENVIRONMENT}" : var.common_info.project
  k8s_version = "1.17"
  worker_nodes_instance_type = "t3.medium"
  min_worker_nodes = var.CURRENT_ENVIRONMENT == "dev" ? 4 : 9
  max_worker_nodes = var.CURRENT_ENVIRONMENT == "dev" ? 5 : 10
  eks_workers_security_group_name = var.CURRENT_ENVIRONMENT == "dev" ? "${var.common_info.project}-${var.CURRENT_ENVIRONMENT}-eks_worker_sg" : "${var.common_info.project}-eks_worker_sg"

  // EKS cluster access key local variables
  ssh_key_name = var.CURRENT_ENVIRONMENT == "dev" ? "${var.common_info.project}-${var.CURRENT_ENVIRONMENT}-eks-key" : "${var.common_info.project}-eks-key"

  // S3 bucket with EKS cluster info local variables
  bucket_name = var.CURRENT_ENVIRONMENT == "dev" ? "${var.common_info.project}-${var.CURRENT_ENVIRONMENT}-eks" : "${var.common_info.project}-eks"
}
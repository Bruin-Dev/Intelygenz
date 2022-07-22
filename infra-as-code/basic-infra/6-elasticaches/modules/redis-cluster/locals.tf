locals {
  // automation-redis local vars
  automation-redis-cluster_id = var.CURRENT_ENVIRONMENT == "dev" ? "${var.REDIS_CLUSTER_NAME}-${var.ENVIRONMENT}" : var.REDIS_CLUSTER_NAME
  automation-redis-cluster-tag-Name = var.CURRENT_ENVIRONMENT == "dev" ? "${var.REDIS_CLUSTER_NAME}-${var.ENVIRONMENT}" : var.REDIS_CLUSTER_NAME

  automation-redis-subnet_group-name = var.CURRENT_ENVIRONMENT == "dev" ? "${var.REDIS_CLUSTER_NAME}-${var.ENVIRONMENT}" : var.REDIS_CLUSTER_NAME

  automation-redis-security_group-Name = var.CURRENT_ENVIRONMENT == "dev" ? "${var.REDIS_CLUSTER_NAME}-${var.ENVIRONMENT}-sg" : "${var.REDIS_CLUSTER_NAME}-sg"
  automation-redis-security_group-tag-Name = var.CURRENT_ENVIRONMENT == "dev" ? "${var.REDIS_CLUSTER_NAME}-${var.ENVIRONMENT}" : var.REDIS_CLUSTER_NAME

  automation-private-zone-Name = var.CURRENT_ENVIRONMENT == "dev" ? "dev.mettel-automation.net." : "pro.mettel-automation.net."

  common_tags = {
    Environment  = var.ENVIRONMENT
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
  }

  // locals from EKS cluster
  eks_workers_security_group_name = var.CURRENT_ENVIRONMENT == "dev" ? "${var.common_info.project}-${var.CURRENT_ENVIRONMENT}-eks_worker_sg" : "${var.common_info.project}-eks_worker_sg"
}
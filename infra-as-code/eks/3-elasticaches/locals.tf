locals {
  // automation-redis local vars
  automation-redis-cluster_id = var.CURRENT_ENVIRONMENT == "dev" ? "${var.common_info.project}-${var.ENVIRONMENT}" : var.common_info.project
  automation-redis-cluster-tag-Name = var.CURRENT_ENVIRONMENT == "dev" ? "${var.common_info.project}-${var.ENVIRONMENT}" : var.common_info.project
  automation-redis-subnet_group-name = var.CURRENT_ENVIRONMENT == "dev" ? "${var.common_info.project}-${var.ENVIRONMENT}" : var.common_info.project
  automation-redis-security_group-name = var.CURRENT_ENVIRONMENT == "dev" ? "${var.common_info.project}-${var.ENVIRONMENT}-sg" : "${var.common_info.project}-sg"
  automation-redis-security_group-tag-Name = var.CURRENT_ENVIRONMENT == "dev" ? "${var.common_info.project}-${var.ENVIRONMENT}" : var.common_info.project
  redis-hostname = aws_elasticache_cluster.automation-redis.cache_nodes[0].address

  // automation-redis-customer-cache local vars
  automation-redis-customer-cache-cluster_id = var.CURRENT_ENVIRONMENT == "dev" ? "${var.common_info.project}-customer-cache-${var.ENVIRONMENT}" : "${var.common_info.project}-customer-cache"
  automation-redis-customer-cache-tag-Name = var.CURRENT_ENVIRONMENT == "dev" ? "${var.common_info.project}-customer-cache-${var.ENVIRONMENT}" : "${var.common_info.project}-customer-cache"
  automation-redis-customer-cache-subnet_group-name = var.CURRENT_ENVIRONMENT == "dev" ? "${var.common_info.project}-customer-cache-${var.ENVIRONMENT}" : "${var.common_info.project}-customer-cache"
  automation-redis-customer-cache-security_group-name = var.CURRENT_ENVIRONMENT == "dev" ? "${var.common_info.project}-customer-cache-${var.ENVIRONMENT}-sg" : "${var.common_info.project}-customer-cache-sg"
  automation-redis-customer-cache-security_group-tag-Name = var.CURRENT_ENVIRONMENT == "dev" ? "${var.common_info.project}-customer-cache-${var.ENVIRONMENT}" : "${var.common_info.project}-customer-cache"
  redis-customer-cache-hostname = aws_elasticache_cluster.automation-redis-customer-cache.cache_nodes[0].address

  // automation-redis-tnba-feedback local vars
  automation-redis-tnba-feedback-cluster_id = var.CURRENT_ENVIRONMENT == "dev" ? "${var.common_info.project}-tnba-feedback-${var.ENVIRONMENT}" : "${var.common_info.project}-tnba-feedback"
  automation-redis-tnba-feedback-tag-Name = var.CURRENT_ENVIRONMENT == "dev" ? "${var.common_info.project}-tnba-feedback-${var.ENVIRONMENT}" : "${var.common_info.project}-tnba-feedback"
  automation-redis-tnba-feedback-subnet_group-name = var.CURRENT_ENVIRONMENT == "dev" ? "${var.common_info.project}-tnba-feedback-${var.ENVIRONMENT}" : "${var.common_info.project}-tnba-feedback"
  automation-redis-tnba-feedback-security_group-name = var.CURRENT_ENVIRONMENT == "dev" ? "${var.common_info.project}-tnba-feedback-${var.ENVIRONMENT}-sg" : "${var.common_info.project}-tnba-feedback-sg"
  automation-redis-tnba-feedback-security_group-tag-Name = var.CURRENT_ENVIRONMENT == "dev" ? "${var.common_info.project}-tnba-feedback-${var.ENVIRONMENT}" : "${var.common_info.project}-tnba-feedback"
  redis-tnba-feedback-hostname = aws_elasticache_cluster.automation-redis-tnba-feedback.cache_nodes[0].address

  // kre local vars
  nginx_ingress_sg_tag_key = var.CURRENT_ENVIRONMENT == "dev" ? "tag:kubernetes.io/cluster/${var.common_info.project}-kre-dev" : "tag:kubernetes.io/cluster/${var.common_info.project}-kre"
  nginx_ingress_sg_tag_value = "owned"

  // eks local vars
  eks_workers_security_group_name = var.CURRENT_ENVIRONMENT == "dev" ? "${var.common_info.project}-${var.CURRENT_ENVIRONMENT}-eks_worker_sg" : "${var.common_info.project}-eks_worker_sg"
}

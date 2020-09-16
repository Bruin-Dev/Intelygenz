module "redis-customer-cache" {
  source = "../modules/redis-cluster"

  CURRENT_ENVIRONMENT = var.CURRENT_ENVIRONMENT
  ENVIRONMENT         = var.ENVIRONMENT
  REDIS_CLUSTER_NAME  = "mettel-automation-customer-cache"
  REDIS_TYPE          = "general"
}
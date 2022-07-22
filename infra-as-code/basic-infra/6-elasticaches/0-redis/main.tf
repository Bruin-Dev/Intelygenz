module "redis" {
  source = "../modules/redis-cluster"

  CURRENT_ENVIRONMENT = var.CURRENT_ENVIRONMENT
  ENVIRONMENT         = var.ENVIRONMENT
  REDIS_CLUSTER_NAME  = "mettel-automation"
  REDIS_TYPE          = "general"
}
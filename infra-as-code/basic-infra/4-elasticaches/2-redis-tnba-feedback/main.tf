module "redis-tnba-feedback" {
  source = "../modules/redis-cluster"

  CURRENT_ENVIRONMENT = var.CURRENT_ENVIRONMENT
  ENVIRONMENT         = var.ENVIRONMENT
  REDIS_CLUSTER_NAME  = "mettel-automation-tnba-feedback"
  REDIS_TYPE          = "specific_for_microservices"
}
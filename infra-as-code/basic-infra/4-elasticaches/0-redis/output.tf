output "REDIS_HOSTNAME" {
  value = module.redis.REDIS_HOSTNAME
  description = "Hostname of redis cluster used for all microservices"
}
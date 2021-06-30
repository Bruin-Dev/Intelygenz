output "REDIS_CUSTOMER_CACHE_HOSTNAME" {
  description = "Hostname of Redis customer-cache"
  value = module.redis-customer-cache.REDIS_HOSTNAME
}
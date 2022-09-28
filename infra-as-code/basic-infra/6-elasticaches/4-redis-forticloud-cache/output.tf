output "REDIS_FORTICLOUD_CACHE_HOSTNAME" {
  description = "Hostname of Redis forticloud-cache"
  value = module.redis-forticloud-cache.REDIS_HOSTNAME
}
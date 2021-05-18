# private DNS to access REDIS from kubernetes cluster
resource "aws_route53_record" "automation-redis-private-name" {
  zone_id = data.aws_route53_zone.mettel-automation-private-zone.zone_id
  name = "redis-${var.REDIS_CLUSTER_NAME}.${local.automation-private-zone-Name}"
  type = "CNAME"
  ttl = "300"
  records = [aws_elasticache_cluster.automation-redis.cache_nodes[0].address]
}
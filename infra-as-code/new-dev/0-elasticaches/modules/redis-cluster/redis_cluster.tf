resource "aws_elasticache_cluster" "automation-redis" {
  cluster_id = local.automation-redis-cluster_id
  engine = "redis"
  engine_version = "5.0.4"
  node_type = var.redis_node_type[var.REDIS_TYPE][var.CURRENT_ENVIRONMENT]
  num_cache_nodes = 1
  parameter_group_name = "default.redis5.0"
  port = 6379
  apply_immediately = true
  subnet_group_name = aws_elasticache_subnet_group.automation-redis-subnet.id
  security_group_ids = [
    aws_security_group.automation-redis-sg.id
  ]
  availability_zone = "us-east-1a"

  tags = merge(local.common_tags, {
    Name          = local.automation-redis-cluster-tag-Name
  })
}

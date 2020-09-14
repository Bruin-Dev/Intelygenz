resource "aws_elasticache_subnet_group" "automation-redis-subnet-customer-cache" {
  count = var.customer_cache_desired_tasks > 0 ? 1 : 0

  name = local.automation-redis-customer-cache-subnet_group-name
  subnet_ids = [
    data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1a.id,
    data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1b.id]
}

resource "aws_elasticache_cluster" "automation-redis-customer-cache" {
  count = var.customer_cache_desired_tasks > 0 ? 1 : 0

  cluster_id = local.automation-redis-customer-cache-cluster_id
  engine = "redis"
  engine_version = "5.0.4"
  node_type = var.redis_node_type_cache_for_microservices[var.CURRENT_ENVIRONMENT]
  num_cache_nodes = 1
  parameter_group_name = "default.redis5.0"
  port = 6379
  apply_immediately = true
  subnet_group_name = aws_elasticache_subnet_group.automation-redis-subnet-customer-cache[0].id
  security_group_ids = [
    aws_security_group.automation-redis-customer-cache-sg[0].id]
  availability_zone = "us-east-1a"

  tags = {
    Name = local.automation-redis-customer-cache-elasticache_cluster-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_security_group" "automation-redis-customer-cache-sg" {
  count = var.customer_cache_desired_tasks > 0 ? 1 : 0

  name = local.automation-redis-customer-cache-security_group-name
  vpc_id = data.terraform_remote_state.tfstate-network-resources.outputs.vpc_automation_id
  description = "Access control to redis customer-cache"

  egress {
    from_port = 0
    protocol = "-1"
    to_port = 0
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port = 6379
    protocol = "tcp"
    to_port = 6379
    cidr_blocks = [
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1a.cidr_block,
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1b.cidr_block
    ]
  }

  tags = {
    Name = local.automation-redis-customer-cache-security_group-tag-Name
    Environment = var.ENVIRONMENT
  }
}

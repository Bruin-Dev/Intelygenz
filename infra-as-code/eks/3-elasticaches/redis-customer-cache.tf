resource "aws_security_group" "automation-redis-customer-cache-sg" {
  name = local.automation-redis-customer-cache-security_group-name
  vpc_id = data.aws_vpc.mettel-automation-vpc.id
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
    security_groups = [
      data.aws_security_group.workers_security_group_eks.id
    ]
  }

  tags = {
    Name          = local.automation-redis-customer-cache-security_group-tag-Name
    Environment   = var.ENVIRONMENT
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
  }
}

resource "aws_elasticache_subnet_group" "automation-redis-customer-cache-subnet" {
  name = local.automation-redis-customer-cache-subnet_group-name
  subnet_ids = data.aws_subnet_ids.mettel-automation-private-subnets.ids
}

resource "aws_elasticache_cluster" "automation-redis-customer-cache" {
  cluster_id = local.automation-redis-customer-cache-cluster_id
  engine = "redis"
  engine_version = "5.0.4"
  node_type = var.redis_node_type[var.CURRENT_ENVIRONMENT]
  num_cache_nodes = 1
  parameter_group_name = "default.redis5.0"
  port = 6379
  apply_immediately = true
  subnet_group_name = aws_elasticache_subnet_group.automation-redis-subnet.id
  security_group_ids = [
    aws_security_group.automation-redis-customer-cache-sg.id
  ]
  availability_zone = "us-east-1a"

  tags = {
    Name          = local.automation-redis-customer-cache-tag-Name
    Environment   = var.ENVIRONMENT
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
  }
}
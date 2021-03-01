locals {
  // automation-redis local vars
  automation-redis-elasticache_cluster-tag-Name = "${var.ENVIRONMENT}-redis"
  automation-redis-security_group-name = "${var.ENVIRONMENT}-redis-sg"
  automation-redis-security_group-tag-Name = "${var.ENVIRONMENT}-redis"
  redis-hostname = aws_elasticache_cluster.automation-redis.cache_nodes[0].address
}

resource "aws_elasticache_cluster" "automation-redis" {
  cluster_id = var.ENVIRONMENT
  engine = "redis"
  engine_version = "5.0.4"
  node_type = var.redis_node_type[var.CURRENT_ENVIRONMENT]
  num_cache_nodes = 1
  parameter_group_name = "default.redis5.0"
  port = 6379
  apply_immediately = true
  subnet_group_name = aws_elasticache_subnet_group.automation-redis-subnet.id
  security_group_ids = [
    aws_security_group.automation-redis-sg.id]
  availability_zone = "us-east-1a"

  tags = {
    Name = local.automation-redis-elasticache_cluster-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_elasticache_subnet_group" "automation-redis-subnet" {
  name = "${var.ENVIRONMENT}-redis-subnet"
  subnet_ids = data.aws_subnet_ids.mettel-automation-public-subnets.ids
}

resource "aws_security_group" "automation-redis-sg" {
  name = local.automation-redis-security_group-name
  vpc_id = data.aws_vpc.mettel-automation-vpc.id
  description = "Access control to redis cache"

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
      data.aws_subnet.mettel-automation-private-subnet-1a.cidr_block,
      data.aws_subnet.mettel-automation-private-subnet-1b.cidr_block
    ]
  }

  tags = {
    Name = local.automation-redis-security_group-tag-Name
    Environment = var.ENVIRONMENT
  }
}

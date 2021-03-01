locals {
  // automation-redis-email-tagger-cache local vars
  automation-redis-email-tagger-cluster_id = "${var.ENVIRONMENT}-email-tagger-cache-redis"
  automation-redis-email-tagger-elasticache_cluster-tag-Name = "${var.ENVIRONMENT}-email-tagger-redis"
  automation-redis-email-tagger-subnet_group-name = "${var.ENVIRONMENT}-email-tagger-redis-subnet"
  automation-redis-email-tagger-security_group-name = "${var.ENVIRONMENT}-email-tagger-redis-sg"
  automation-redis-email-tagger-security_group-tag-Name = "${var.ENVIRONMENT}-email-tagger-redis"
  automation-redis-email-tagger-hostname = aws_elasticache_cluster.automation-redis-email-tagger[0].cache_nodes[0].address
}

resource "aws_elasticache_subnet_group" "automation-redis-subnet-email-tagger" {
  count = var.email_tagger_monitor_desired_tasks > 0 ? 1 : 0

  name = local.automation-redis-email-tagger-subnet_group-name
  subnet_ids = data.aws_subnet_ids.mettel-automation-public-subnets.ids
}

resource "aws_elasticache_cluster" "automation-redis-email-tagger" {
  count = var.email_tagger_monitor_desired_tasks > 0 ? 1 : 0

  cluster_id = local.automation-redis-email-tagger-cluster_id
  engine = "redis"
  engine_version = "5.0.4"
  node_type = var.redis_node_type_cache_for_microservices[var.CURRENT_ENVIRONMENT]
  num_cache_nodes = 1
  parameter_group_name = "default.redis5.0"
  port = 6379
  apply_immediately = true
  subnet_group_name = aws_elasticache_subnet_group.automation-redis-subnet-email-tagger[0].id
  security_group_ids = [
    aws_security_group.automation-redis-email-tagger-sg[0].id]
  availability_zone = "us-east-1a"

  tags = {
    Name = local.automation-redis-email-tagger-elasticache_cluster-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_security_group" "automation-redis-email-tagger-sg" {
  count = var.email_tagger_monitor_desired_tasks > 0 ? 1 : 0

  name = local.automation-redis-email-tagger-security_group-name
  vpc_id = data.aws_vpc.mettel-automation-vpc.id
  description = "Access control to redis email-tagger"

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
    Name = local.automation-redis-email-tagger-security_group-tag-Name
    Environment = var.ENVIRONMENT
  }
}

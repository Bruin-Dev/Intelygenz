resource "aws_elasticache_cluster" "automation-redis" {
  cluster_id = "${var.ENVIRONMENT}"
  engine = "redis"
  engine_version = "5.0.4"
  node_type = "cache.m4.large"
  num_cache_nodes = 1
  parameter_group_name = "default.redis5.0"
  port = 6379
  apply_immediately = true
  subnet_group_name = "${aws_elasticache_subnet_group.automation-redis-subnet.id}"
  security_group_ids = ["${aws_security_group.automation-redis-sg.id}"]
  availability_zone = "us-east-1a"

  tags = {
    Name = "${var.ENVIRONMENT}-redis"
  }
}

resource "aws_elasticache_subnet_group" "automation-redis-subnet" {
  name = "${var.ENVIRONMENT}-redis-subnet"
  subnet_ids = [
    "${aws_subnet.automation-private_subnet-1a.id}"]
}

resource "aws_security_group" "automation-redis-sg" {
  name = "${var.ENVIRONMENT}-redis-sg"
  vpc_id = "${aws_vpc.automation-vpc.id}"
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
    "${aws_subnet.automation-private_subnet-1a.cidr_block}"
    ]
  }

  tags = {
    Name = "${var.ENVIRONMENT}-redis"
  }
}

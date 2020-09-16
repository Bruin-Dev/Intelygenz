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
    security_groups = [
      data.aws_security_group.workers_security_group_eks.id
    ]
  }

  tags = merge(local.common_tags, {
    Name = local.automation-redis-security_group-tag-Name
  })
}


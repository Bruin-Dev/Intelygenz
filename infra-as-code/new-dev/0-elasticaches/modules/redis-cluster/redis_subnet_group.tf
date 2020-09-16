resource "aws_elasticache_subnet_group" "automation-redis-subnet" {
  name = local.automation-redis-subnet_group-name
  subnet_ids = data.aws_subnet_ids.mettel-automation-private-subnets.ids
}
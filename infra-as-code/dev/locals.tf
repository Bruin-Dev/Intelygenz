locals {
  // common vars for dev project
  log_prefix = "${var.ENVIRONMENT}-${var.BUILD_NUMBER}"

  // automation-alb local vars
  automation-dev-inbound-security_group-name = "${var.ENVIRONMENT}-inbound"
  automation-dev-inbound-security_group-tag-Name = "${var.ENVIRONMENT}-inbound"

  // dns local vars
  automation-route53_record-name = "${var.SUBDOMAIN}.${data.aws_route53_zone.automation.name}"
  automation-zone-service_discovery_private_dns-name = "${var.ENVIRONMENT}.local"

  // automation-nats-server local vars
  automation-nats-server-image = "${data.aws_ecr_repository.automation-nats-server.repository_url}:${var.NATS_MODULE_VERSION}"
  automation-nats-server-ecs_task_definition-family = "${var.ENVIRONMENT}-nats-server"
  automation-nats_service-security_group-name = "${var.ENVIRONMENT}-nats-server"
  automation-nats_service-security_group-tag-Name = "${var.ENVIRONMENT}-nats-server"
  automation-nats-server-ecs_service-name = "${var.ENVIRONMENT}-nats-server"
  automation-nats-server-ecs_service-task_definition = "${aws_ecs_task_definition.automation-nats-server.family}:${aws_ecs_task_definition.automation-nats-server.revision}"

  // automation-redis local vars
  automation-redis-elasticache_cluster-tag-Name = "${var.ENVIRONMENT}-redis"
  automation-redis-security_group-name = "${var.ENVIRONMENT}-redis-sg"
  automation-redis-security_group-tag-Name = "${var.ENVIRONMENT}-redis"

  // automation-vpc local vars
  automation-nat_eip-1a-tag-Name = "${var.ENVIRONMENT}-nat-1a"
  automation-nat_eip-1b-tag-Name = "${var.ENVIRONMENT}-nat-1b"
  automation-nat_gateway-1a-tag-Name = "${var.ENVIRONMENT}-1a"
  automation-nat_gateway-1b-tag-Name = "${var.ENVIRONMENT}-1b"
  automation-public_subnet-1a-tag-Name = "${var.ENVIRONMENT}-public-subnet-1a"
  automation-public_subnet-1b-tag-Name = "${var.ENVIRONMENT}-public-subnet-1b"
  automation-private_subnet-1a-subnet-cidr_block = "${var.cdir_private_1}/24"
  automation-private_subnet-1a-tag-Name = "${var.ENVIRONMENT}-private-subnet-1a"
  automation-private_subnet-1b-tag-Name = "${var.ENVIRONMENT}-private-subnet-1b"
  automation-private-route_table-tag-Name = "${var.ENVIRONMENT}-private-route-table"
  automation-public-route_table-tag-Name = "${var.ENVIRONMENT}-public-route-table"
  automation-default-security_group-tag-Name = "${var.ENVIRONMENT}-default"
}
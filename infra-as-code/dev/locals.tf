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
  automation-nats-server-nats_service-security_group-name = "${var.ENVIRONMENT}-nats-server"
  automation-nats-server-nats_service-security_group-tag-Name = "${var.ENVIRONMENT}-nats-server"
  automation-nats-server-ecs_service-name = "${var.ENVIRONMENT}-nats-server"
  automation-nats-server-ecs_service-task_definition = "${aws_ecs_task_definition.automation-nats-server.family}:${aws_ecs_task_definition.automation-nats-server.revision}"
  automation-nats-server-task_definition_template-container_name = "nats-server"
  automation-nats-server-task_definition_template-natscluster = "nats://0.0.0.0:${var.NATS_SERVER_SEED_CLUSTER_PORT}"

  // automation-redis local vars
  automation-redis-elasticache_cluster-tag-Name = "${var.ENVIRONMENT}-redis"
  automation-redis-security_group-name = "${var.ENVIRONMENT}-redis-sg"
  automation-redis-security_group-tag-Name = "${var.ENVIRONMENT}-redis"
}

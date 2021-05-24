locals {
   // automation-queue-forwarder local vars
  automation-queue-forwarder-image = "${data.aws_ecr_repository.automation-queue-forwarder.repository_url}:${data.external.queue-forwarder-build_number.result["image_tag"]}"
  automation-queue-forwarder-papertrail_prefix = "queue-forwarder-${element(split("-", data.external.queue-forwarder-build_number.result["image_tag"]),2)}"
  automation-queue-forwarder-ecs_task_definition-family = "${var.ENVIRONMENT}-queue-forwarder"
  automation-queue-forwarder-service-security_group-name = "${var.ENVIRONMENT}-queue-forwarder"
  automation-queue-forwarder-service-security_group-tag-Name = "${var.ENVIRONMENT}-queue-forwarder"
  automation-queue-forwarder-ecs_service-name = "${var.ENVIRONMENT}-queue-forwarder"
  automation-queue-forwarder-ecs_service-task_definition = "${aws_ecs_task_definition.automation-queue-forwarder.family}:${aws_ecs_task_definition.automation-queue-forwarder.revision}"
  automation-queue-forwarder-service_discovery_service-name = "queue-forwarder-${var.ENVIRONMENT}"
}

data "aws_ecr_repository" "automation-queue-forwarder" {
  name = "automation-queue-forwarder"
}

data "external" "queue-forwarder-build_number" {
  program = [
    "bash",
    "${path.module}/scripts/obtain_latest_image_for_repository.sh",
    data.aws_ecr_repository.automation-queue-forwarder.name
  ]
}

data "template_file" "automation-queue-forwarder" {
  template = file("${path.module}/task-definitions/queue_forwarder.json")

  vars = {
    image = local.automation-queue-forwarder-image
    log_group = var.ENVIRONMENT
    log_prefix = local.log_prefix

    PYTHONUNBUFFERED = var.PYTHONUNBUFFERED
    NATS_SERVER1 = local.nats_server1
    REDIS_HOSTNAME = local.redis-hostname
    CURRENT_ENVIRONMENT = var.CURRENT_ENVIRONMENT
    PAPERTRAIL_ACTIVE = var.CURRENT_ENVIRONMENT == "production" ? true : false
    PAPERTRAIL_PREFIX = local.automation-queue-forwarder-papertrail_prefix
    PAPERTRAIL_HOST = var.PAPERTRAIL_HOST
    PAPERTRAIL_PORT = var.PAPERTRAIL_PORT
    ENVIRONMENT_NAME = var.ENVIRONMENT_NAME
  }
}

resource "aws_ecs_task_definition" "automation-queue-forwarder" {
  family = local.automation-queue-forwarder-ecs_task_definition-family
  container_definitions = data.template_file.automation-queue-forwarder.rendered
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "256"
  memory = "512"
  execution_role_arn = data.aws_iam_role.ecs_execution_role.arn
  task_role_arn = data.aws_iam_role.ecs_execution_role.arn
}

resource "aws_security_group" "automation-queue-forwarder_service" {
  vpc_id = data.aws_vpc.mettel-automation-vpc.id
  name = local.automation-queue-forwarder-service-security_group-name
  description = "Allow egress from container"

  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = [
      "0.0.0.0/0"]
  }

  ingress {
    from_port = 8
    to_port = 0
    protocol = "icmp"
    cidr_blocks = [
      "0.0.0.0/0"]
  }

  ingress {
    from_port = 5000
    to_port = 5000
    protocol = "TCP"
    cidr_blocks = [
      "0.0.0.0/0"
    ]
  }

  ingress {
    from_port = 9090
    to_port = 9090
    protocol = "TCP"
    cidr_blocks = [
      data.aws_vpc.mettel-automation-vpc.cidr_block
    ]
  }

  tags = {
    Name = local.automation-queue-forwarder-service-security_group-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_service_discovery_service" "queue-forwarder" {
  name = local.automation-queue-forwarder-service_discovery_service-name

  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.automation-zone.id

    dns_records {
      ttl = 10
      type = "A"
    }

    routing_policy = "MULTIVALUE"
  }

  health_check_custom_config {
    failure_threshold = 1
  }
}

resource "aws_ecs_service" "automation-queue-forwarder" {
  name = local.automation-queue-forwarder-ecs_service-name
  task_definition = local.automation-queue-forwarder-ecs_service-task_definition
  desired_count = var.queue_forwarder_desired_tasks
  launch_type = "FARGATE"
  cluster = aws_ecs_cluster.automation.id
  count = var.queue_forwarder_desired_tasks != 0 ? 1 : 0

  network_configuration {
    security_groups = [
      aws_security_group.automation-queue-forwarder_service.id]
    subnets = data.aws_subnet_ids.mettel-automation-private-subnets.ids
    assign_public_ip = false
  }

  service_registries {
    registry_arn = aws_service_discovery_service.queue-forwarder.arn
  }

  depends_on = [ null_resource.bruin-bridge-healthcheck,
                 null_resource.cts-bridge-healthcheck,
                 null_resource.digi-bridge-healthcheck,
                 null_resource.email-tagger-kre-bridge-healthcheck,
                 null_resource.hawkeye-bridge-healthcheck,
                 null_resource.lit-bridge-healthcheck,
                 null_resource.metrics-prometheus-healthcheck,
                 null_resource.notifier-healthcheck,
                 null_resource.t7-bridge-healthcheck,
                 null_resource.velocloud-bridge-healthcheck]
}

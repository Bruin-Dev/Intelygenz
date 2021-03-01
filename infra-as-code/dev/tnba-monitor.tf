locals {
  // automation-tnba-monitor local vars
  automation-tnba-monitor-image = "${data.aws_ecr_repository.automation-tnba-monitor.repository_url}:${data.external.tnba-monitor-build_number.result["image_tag"]}"
  automation-tnba-monitor-log_prefix = "${var.ENVIRONMENT}-${var.BUILD_NUMBER}"
  automation-tnba-monitor-ecs_task_definition-family = "${var.ENVIRONMENT}-tnba-monitor"
  automation-tnba-monitor-service-security_group-name = "${var.ENVIRONMENT}-tnba-monitor"
  automation-tnba-monitor-service-security_group-tag-Name = "${var.ENVIRONMENT}-tnba-monitor"
  automation-tnba-monitor-ecs_service-name = "${var.ENVIRONMENT}-tnba-monitor"
  automation-tnba-monitor-ecs_service-task_definition = "${aws_ecs_task_definition.automation-tnba-monitor.family}:${aws_ecs_task_definition.automation-tnba-monitor.revision}"
  automation-tnba-monitor-service_discovery_service-name = "tnba-monitor-${var.ENVIRONMENT}"
  automation-tnba-monitor-papertrail_prefix = "tnba-monitor-${element(split("-", data.external.tnba-monitor-build_number.result["image_tag"]),2)}"
}

data "aws_ecr_repository" "automation-tnba-monitor" {
  name = "automation-tnba-monitor"
}

data "external" "tnba-monitor-build_number" {
  program = [
    "bash",
    "${path.module}/scripts/obtain_latest_image_for_repository.sh",
    data.aws_ecr_repository.automation-tnba-monitor.name
  ]
}

data "template_file" "automation-tnba-monitor" {
  template = file("${path.module}/task-definitions/tnba_monitor.json")

  vars = {
    image = local.automation-tnba-monitor-image
    log_group = var.ENVIRONMENT
    log_prefix = local.automation-tnba-monitor-log_prefix

    PYTHONUNBUFFERED = var.PYTHONUNBUFFERED
    NATS_SERVER1 = local.nats_server1
    REDIS_HOSTNAME = local.redis-hostname
    CURRENT_ENVIRONMENT = var.CURRENT_ENVIRONMENT
    PAPERTRAIL_ACTIVE = var.CURRENT_ENVIRONMENT == "production" ? true : false
    PAPERTRAIL_PREFIX = local.automation-tnba-monitor-papertrail_prefix
    PAPERTRAIL_HOST = var.PAPERTRAIL_HOST
    PAPERTRAIL_PORT = var.PAPERTRAIL_PORT
    ENVIRONMENT_NAME = var.ENVIRONMENT_NAME
  }
}

resource "aws_ecs_task_definition" "automation-tnba-monitor" {
  family = local.automation-tnba-monitor-ecs_task_definition-family
  container_definitions = data.template_file.automation-tnba-monitor.rendered
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "256"
  memory = "512"
  execution_role_arn = data.aws_iam_role.ecs_execution_role.arn
  task_role_arn = data.aws_iam_role.ecs_execution_role.arn
}

resource "aws_security_group" "automation-tnba-monitor_service" {
  vpc_id = data.aws_vpc.mettel-automation-vpc.id
  name = local.automation-tnba-monitor-service-security_group-name
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

  tags = {
    Name = local.automation-tnba-monitor-service-security_group-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_service_discovery_service" "tnba-monitor" {
  name = local.automation-tnba-monitor-service_discovery_service-name

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

resource "aws_ecs_service" "automation-tnba-monitor" {
  name = local.automation-tnba-monitor-ecs_service-name
  task_definition = local.automation-tnba-monitor-ecs_service-task_definition
  desired_count = var.tnba_monitor_desired_tasks
  launch_type = "FARGATE"
  cluster = aws_ecs_cluster.automation.id
  count = var.tnba_monitor_desired_tasks != 0 ? 1 : 0

  network_configuration {
    security_groups = [
      aws_security_group.automation-tnba-monitor_service.id]
    subnets = data.aws_subnet_ids.mettel-automation-private-subnets.ids
    assign_public_ip = false
  }

  service_registries {
    registry_arn = aws_service_discovery_service.tnba-monitor.arn
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

## ticket-collector local variables
locals {
  // automation-ticket-collector local vars
  automation-ticket-collector-image = "${data.aws_ecr_repository.automation-ticket-collector.repository_url}:${data.external.ticket-collector-build_number.result["image_tag"]}"
  automation-ticket-collector-papertrail_prefix = "ticket-collector-${element(split("-", data.external.ticket-collector-build_number.result["image_tag"]),2)}"
  automation-ticket-collector-ecs_task_definition-family = "${var.ENVIRONMENT}-ticket-collector"
  automation-ticket-collector_service-security_group-name = "${var.ENVIRONMENT}-ticket-collector"
  automation-ticket-collector-resource-name = "${var.ENVIRONMENT}-ticket-collector"
  automation-ticket-collector-service-security_group-tag-Name = "${var.ENVIRONMENT}-ticket-collector"
  automation-ticket-collector-task_definition = "${aws_ecs_task_definition.automation-ticket-collector.family}:${aws_ecs_task_definition.automation-ticket-collector.revision}"
  automation-ticket-collector-service_discovery_service-name = "ticket-collector-${var.ENVIRONMENT}"
}

data "aws_ecr_repository" "automation-ticket-collector" {
  name = "automation-ticket-collector"
}

data "external" "ticket-collector-build_number" {
  program = [
    "bash",
    "${path.module}/scripts/obtain_latest_image_for_repository.sh",
    data.aws_ecr_repository.automation-ticket-collector.name
  ]
}

data "template_file" "automation-ticket-collector" {
  template = file("${path.module}/task-definitions/ticket_collector.json")

  vars = {
    image = local.automation-ticket-collector-image
    log_group = var.ENVIRONMENT
    log_prefix = local.log_prefix

    MONGODB_USERNAME = var.MONGODB_USERNAME
    MONGODB_PASSWORD = var.MONGODB_PASSWORD
    MONGODB_HOST = var.MONGODB_HOST
    MONGODB_DATABASE = var.MONGODB_DATABASE
    INTERVAL_TASKS_RUN = var.INTERVAL_TASKS_RUN
    BRUIN_CLIENT_ID = var.BRUIN_CLIENT_ID
    BRUIN_CLIENT_SECRET = var.BRUIN_CLIENT_SECRET
    CURRENT_ENVIRONMENT = var.CURRENT_ENVIRONMENT
    ENVIRONMENT_NAME = var.ENVIRONMENT_NAME
    PAPERTRAIL_ACTIVE = var.CURRENT_ENVIRONMENT == "production" ? true : false
    PAPERTRAIL_PREFIX = local.automation-ticket-collector-papertrail_prefix
    PAPERTRAIL_HOST = var.PAPERTRAIL_HOST
    PAPERTRAIL_PORT = var.PAPERTRAIL_PORT
  }
}

resource "aws_ecs_task_definition" "automation-ticket-collector" {
  family = local.automation-ticket-collector-ecs_task_definition-family
  container_definitions = data.template_file.automation-ticket-collector.rendered
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "256"
  memory = "512"
  execution_role_arn = data.aws_iam_role.ecs_execution_role.arn
  task_role_arn = data.aws_iam_role.ecs_execution_role.arn
}

resource "aws_security_group" "automation-ticket-collector_service" {
  vpc_id = data.aws_vpc.mettel-automation-vpc.id
  name = local.automation-ticket-collector_service-security_group-name
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

  tags = {
    Name = local.automation-ticket-collector-service-security_group-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_service_discovery_service" "ticket-collector" {
  name = local.automation-ticket-collector-service_discovery_service-name

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

resource "aws_ecs_service" "automation-ticket-collector" {
  name = local.automation-ticket-collector-resource-name
  task_definition = local.automation-ticket-collector-task_definition
  desired_count = var.ticket_collector_desired_tasks
  launch_type = "FARGATE"
  cluster = aws_ecs_cluster.automation.id
  count = var.ticket_collector_desired_tasks != 0 ? 1 : 0

  network_configuration {
    security_groups = [
      aws_security_group.automation-ticket-collector_service.id]
    subnets = data.aws_subnet_ids.mettel-automation-private-subnets.ids
    assign_public_ip = false
  }

  service_registries {
    registry_arn = aws_service_discovery_service.ticket-collector.arn
  }


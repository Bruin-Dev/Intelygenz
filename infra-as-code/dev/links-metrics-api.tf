## links-metrics-api local variables
locals {
  // automation-links-metrics-api local vars
  automation-links-metrics-api-image = "${data.aws_ecr_repository.automation-links-metrics-api[0].repository_url}:${data.external.links-metrics-api-build_number[0].result["image_tag"]}"
  automation-links-metrics-api-papertrail_prefix = "links-metrics-api-${element(split("-", data.external.links-metrics-api-build_number[0].result["image_tag"]),2)}"
  automation-links-metrics-api-ecs_task_definition-family = "${var.ENVIRONMENT}-links-metrics-api"
  automation-links-metrics-api_service-security_group-name = "${var.ENVIRONMENT}-links-metrics-api"
  automation-links-metrics-api-resource-name = "${var.ENVIRONMENT}-links-metrics-api"
  automation-links-metrics-api-service-security_group-tag-Name = "${var.ENVIRONMENT}-links-metrics-api"
  automation-links-metrics-api-task_definition = "${aws_ecs_task_definition.automation-links-metrics-api[0].family}:${aws_ecs_task_definition.automation-links-metrics-api[0].revision}"
  automation-links-metrics-api-service_discovery_service-name = "links-metrics-api-${var.ENVIRONMENT}"
  automation-links-metrics-api-target_group-name = "${var.ENVIRONMENT}-statistics"
  automation-links-metrics-api-target_group-tag-Name = "${var.ENVIRONMENT}-links-metrics-api"
}

data "aws_ecr_repository" "automation-links-metrics-api" {
  count = var.CURRENT_ENVIRONMENT == "production" ? 1 : 0
  name  = "automation-links-metrics-api"
}

data "external" "links-metrics-api-build_number" {
  count   = var.CURRENT_ENVIRONMENT == "production" ? 1 : 0
  program = [
    "bash",
    "${path.module}/scripts/obtain_latest_image_for_repository.sh",
    data.aws_ecr_repository.automation-links-metrics-api[0].name
  ]
}

data "template_file" "automation-links-metrics-api" {
  count    = var.CURRENT_ENVIRONMENT == "production" ? 1 : 0
  template = file("${path.module}/task-definitions/links_metrics_api.json")

  vars = {
    image = local.automation-links-metrics-api-image
    log_group = var.ENVIRONMENT
    log_prefix = local.log_prefix

    NATS_SERVER1 = local.nats_server1
    REDIS_HOSTNAME = local.redis-hostname
    MONGODB_USERNAME = var.TICKET_COLLECTOR_MONGO_USERNAME
    MONGODB_PASSWORD = var.TICKET_COLLECTOR_MONGO_PASSWORD
    MONGODB_HOST = var.TICKET_COLLECTOR_MONGO_HOST
    MONGODB_PORT = var.TICKET_COLLECTOR_MONGO_PORT
    CURRENT_ENVIRONMENT = var.CURRENT_ENVIRONMENT
    ENVIRONMENT_NAME = var.ENVIRONMENT_NAME
    PAPERTRAIL_ACTIVE = var.CURRENT_ENVIRONMENT == "production" ? true : false
    PAPERTRAIL_PREFIX = local.automation-links-metrics-api-papertrail_prefix
    PAPERTRAIL_HOST = var.PAPERTRAIL_HOST
    PAPERTRAIL_PORT = var.PAPERTRAIL_PORT
  }
}

resource "aws_ecs_task_definition" "automation-links-metrics-api" {
  count  = var.CURRENT_ENVIRONMENT == "production" ? 1 : 0
  family = local.automation-links-metrics-api-ecs_task_definition-family
  container_definitions = data.template_file.automation-links-metrics-api[0].rendered
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "256"
  memory = "512"
  execution_role_arn = data.aws_iam_role.ecs_execution_role.arn
  task_role_arn = data.aws_iam_role.ecs_execution_role.arn
}

resource "aws_security_group" "automation-links-metrics-api_service" {
  count = var.CURRENT_ENVIRONMENT == "production" ? 1 : 0
  vpc_id = data.aws_vpc.mettel-automation-vpc.id
  name = local.automation-links-metrics-api_service-security_group-name
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
    Name = local.automation-links-metrics-api-service-security_group-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_ecs_service" "automation-links-metrics-api" {
  count = var.CURRENT_ENVIRONMENT == "production" ? 1 : 0
  name = local.automation-links-metrics-api-resource-name
  task_definition = local.automation-links-metrics-api-task_definition
  desired_count = var.links_metrics_api_desired_tasks
  launch_type = "FARGATE"
  cluster = aws_ecs_cluster.automation.id

  network_configuration {
    security_groups = [
      aws_security_group.automation-links-metrics-api_service[0].id]
    subnets = data.aws_subnet_ids.mettel-automation-private-subnets.ids
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.target_group_oreilly_front_end_ssl[0].arn
    container_name   = "links-metrics-api"
    container_port   = 5000
  }
}
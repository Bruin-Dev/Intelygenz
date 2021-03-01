locals {
  // automation-email-tagger-monitor local vars
  automation-email-tagger-monitor-image = "${data.aws_ecr_repository.automation-email-tagger-monitor.repository_url}:${data.external.email-tagger-monitor-build_number.result["image_tag"]}"
  automation-email-tagger-monitor-papertrail_prefix = "email-tagger-monitor-${element(split("-", data.external.email-tagger-monitor-build_number.result["image_tag"]),2)}"
  automation-email-tagger-monitor-ecs_task_definition-family = "${var.ENVIRONMENT}-email-tagger-monitor"
  automation-email-tagger-monitor-service-security_group-name = "${var.ENVIRONMENT}-email-tagger-monitor"
  automation-email-tagger-monitor-resource-name = "${var.ENVIRONMENT}-email-tagger-monitor"
  automation-email-tagger-monitor-service-security_group-tag-Name = "${var.ENVIRONMENT}-email-tagger-monitor"
  automation-email-tagger-monitor-task_definition = "${aws_ecs_task_definition.automation-email-tagger-monitor.family}:${aws_ecs_task_definition.automation-email-tagger-monitor.revision}"
  automation-email-tagger-monitor-target_group-name = "${var.ENVIRONMENT}-email-tagger"
  automation-email-tagger-monitor-target_group-tag-Name = "${var.ENVIRONMENT}-email-tagger"
  automation-email-tagger-monitor-alb-listener-rules = [
    "${var.EMAIL_TAGGER_MONITOR_API_SERVER_ENDPOINT_PREFIX}*",
    substr(var.EMAIL_TAGGER_MONITOR_API_SERVER_ENDPOINT_PREFIX, 0, (length(var.EMAIL_TAGGER_MONITOR_API_SERVER_ENDPOINT_PREFIX) - 1))
  ]
}

data "aws_ecr_repository" "automation-email-tagger-monitor" {
  name = "automation-email-tagger-monitor"
}

data "external" "email-tagger-monitor-build_number" {
  program = [
    "bash",
    "${path.module}/scripts/obtain_latest_image_for_repository.sh",
    data.aws_ecr_repository.automation-email-tagger-monitor.name
  ]
}

data "template_file" "automation-email-tagger-monitor" {
  template = file("${path.module}/task-definitions/email_tagger_monitor.json")

  vars = {
    image = local.automation-email-tagger-monitor-image
    log_group = var.ENVIRONMENT
    log_prefix = local.log_prefix

    ENVIRONMENT_NAME = var.ENVIRONMENT_NAME
    NATS_SERVER1 = local.nats_server1
    REDIS_HOSTNAME = local.redis-hostname
    REDIS_CACHE_HOSTNAME = local.automation-redis-email-tagger-hostname
    CURRENT_ENVIRONMENT = var.CURRENT_ENVIRONMENT
    REQUEST_SIGNATURE_SECRET_KEY = var.EMAIL_TAGGER_MONITOR_REQUEST_SIGNATURE_SECRET_KEY
    REQUEST_API_KEY = var.EMAIL_TAGGER_MONITOR_REQUEST_API_KEY
    API_SERVER_ENDPOINT_PREFIX = var.EMAIL_TAGGER_MONITOR_API_SERVER_ENDPOINT_PREFIX
    PYTHONUNBUFFERED = var.PYTHONUNBUFFERED
    PAPERTRAIL_ACTIVE = var.CURRENT_ENVIRONMENT == "production" ? true : false
    PAPERTRAIL_PREFIX = local.automation-email-tagger-monitor-papertrail_prefix
    PAPERTRAIL_HOST = var.PAPERTRAIL_HOST
    PAPERTRAIL_PORT = var.PAPERTRAIL_PORT
  }
}

resource "aws_ecs_task_definition" "automation-email-tagger-monitor" {
  family = local.automation-email-tagger-monitor-ecs_task_definition-family
  container_definitions = data.template_file.automation-email-tagger-monitor.rendered
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "256"
  memory = "512"
  execution_role_arn = data.aws_iam_role.ecs_execution_role.arn
  task_role_arn = data.aws_iam_role.ecs_execution_role.arn
}

resource "aws_security_group" "automation-email-tagger-monitor_service" {
  vpc_id = data.aws_vpc.mettel-automation-vpc.id
  name = local.automation-email-tagger-monitor-service-security_group-name
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
    Name = local.automation-email-tagger-monitor-service-security_group-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_ecs_service" "automation-email-tagger-monitor" {
  name = local.automation-email-tagger-monitor-resource-name
  task_definition = local.automation-email-tagger-monitor-task_definition
  desired_count = var.email_tagger_monitor_desired_tasks
  launch_type = "FARGATE"
  cluster = aws_ecs_cluster.automation.id
  count = var.email_tagger_monitor_desired_tasks != 0 ? 1 : 0

  network_configuration {
    security_groups = [
      aws_security_group.automation-email-tagger-monitor_service.id]
    subnets = data.aws_subnet_ids.mettel-automation-private-subnets.ids
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.automation-email-tagger-monitor.arn
    container_name   = "email-tagger-monitor"
    container_port   = 5000
  }

  depends_on = [ null_resource.bruin-bridge-healthcheck,
                 null_resource.cts-bridge-healthcheck,
                 null_resource.digi-bridge-healthcheck,
                 null_resource.email-tagger-kre-bridge-healthcheck,
                 null_resource.lit-bridge-healthcheck,
                 null_resource.metrics-prometheus-healthcheck,
                 null_resource.notifier-healthcheck,
                 null_resource.velocloud-bridge-healthcheck,
                 null_resource.hawkeye-bridge-healthcheck,
                 null_resource.t7-bridge-healthcheck]
}

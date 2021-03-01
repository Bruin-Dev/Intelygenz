locals {
  // automation-last-contact-report local vars
  automation-last-contact-report-ecs_task_definition-family = "${var.ENVIRONMENT}-last-contact-report"
  automation-last-contact-report-image = "${data.aws_ecr_repository.automation-last-contact-report.repository_url}:${data.external.dispatch-portal-backend-build_number.result["image_tag"]}"
  automation-last-contact-report-papertrail_prefix = "last-contact-report-${element(split("-", data.external.dispatch-portal-backend-build_number.result["image_tag"]),2)}"
  automation-last-contact-report-service-security_group-name = "${var.ENVIRONMENT}-last-contact-report"
  automation-last-contact-report-service-security_group-tag-Name = "${var.ENVIRONMENT}-last-contact-report"
  automation-last-contact-report-resource-name = "${var.ENVIRONMENT}-last-contact-report"
  automation-last-contact-report-task_definition = "${aws_ecs_task_definition.automation-last-contact-report.family}:${aws_ecs_task_definition.automation-last-contact-report.revision}"
  automation-last-contact-service_discovery_service-name = "last-contact-report-${var.ENVIRONMENT}"
}

data "aws_ecr_repository" "automation-last-contact-report" {
  name = "automation-last-contact-report"
}

data "external" "last-contact-report-build_number" {
  program = [
    "bash",
    "${path.module}/scripts/obtain_latest_image_for_repository.sh",
    data.aws_ecr_repository.automation-last-contact-report.name
  ]
}

data "template_file" "automation-last-contact-report" {
  template = file("${path.module}/task-definitions/last_contact_report.json")

  vars = {
    image = local.automation-last-contact-report-image
    log_group = var.ENVIRONMENT
    log_prefix = local.log_prefix

    PYTHONUNBUFFERED = var.PYTHONUNBUFFERED
    NATS_SERVER1 = local.nats_server1
    REDIS_HOSTNAME = local.redis-hostname
    LAST_CONTACT_RECIPIENT = var.LAST_CONTACT_RECIPIENT
    PAPERTRAIL_ACTIVE = var.CURRENT_ENVIRONMENT == "production" ? true : false
    PAPERTRAIL_PREFIX = local.automation-last-contact-report-papertrail_prefix
    PAPERTRAIL_HOST = var.PAPERTRAIL_HOST
    PAPERTRAIL_PORT = var.PAPERTRAIL_PORT
    ENVIRONMENT_NAME = var.ENVIRONMENT_NAME
  }
}

resource "aws_ecs_task_definition" "automation-last-contact-report" {
  family = local.automation-last-contact-report-ecs_task_definition-family
  container_definitions = data.template_file.automation-last-contact-report.rendered
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "256"
  memory = "512"
  execution_role_arn = data.aws_iam_role.ecs_execution_role.arn
  task_role_arn = data.aws_iam_role.ecs_execution_role.arn
}

resource "aws_security_group" "automation-last-contact-report_service" {
  vpc_id = data.aws_vpc.mettel-automation-vpc.id
  name = local.automation-last-contact-report-service-security_group-name
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
    Name = local.automation-last-contact-report-service-security_group-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_service_discovery_service" "last-contact-report" {
  name = local.automation-last-contact-service_discovery_service-name

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

resource "aws_ecs_service" "automation-last-contact-report" {
  name = local.automation-last-contact-report-resource-name
  task_definition = local.automation-last-contact-report-task_definition
  desired_count = var.last_contact_report_desired_tasks
  launch_type = "FARGATE"
  cluster = aws_ecs_cluster.automation.id
  count = var.last_contact_report_desired_tasks != 0 ? 1 : 0

  network_configuration {
    security_groups = [
      aws_security_group.automation-last-contact-report_service.id]
    subnets = data.aws_subnet_ids.mettel-automation-private-subnets.ids
    assign_public_ip = false
  }

  service_registries {
    registry_arn = aws_service_discovery_service.last-contact-report.arn
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

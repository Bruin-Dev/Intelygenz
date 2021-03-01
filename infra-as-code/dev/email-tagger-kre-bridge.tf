locals {
  // automation-email-tagger-kre-bridge local vars
  automation-email-tagger-kre-bridge-image = "${data.aws_ecr_repository.automation-email-tagger-kre-bridge.repository_url}:${data.external.email-tagger-kre-bridge-build_number.result["image_tag"]}"
  automation-email-tagger-kre-bridge-papertrail_prefix = "email-tagger-kre-bridge-${element(split("-", data.external.email-tagger-kre-bridge-build_number.result["image_tag"]),2)}"
  automation-email-tagger-kre-bridge-ecs_task_definition-family = "${var.ENVIRONMENT}-email-tagger-kre-bridge"
  automation-email-tagger-kre-bridge-service-security_group-name = "${var.ENVIRONMENT}-email-tagger-kre-bridge"
  automation-email-tagger-kre-bridge-resource-name = "${var.ENVIRONMENT}-email-tagger-kre-bridge"
  automation-email-tagger-kre-bridge-service-security_group-tag-Name = "${var.ENVIRONMENT}-email-tagger-kre-bridge"
  automation-email-tagger-kre-bridge-task_definition = "${aws_ecs_task_definition.automation-email-tagger-kre-bridge.family}:${aws_ecs_task_definition.automation-email-tagger-kre-bridge.revision}"
  automation-email-tagger-kre-bridge-service_discovery_service-name = "email-tagger-kre-bridge-${var.ENVIRONMENT}"
}

data "aws_ecr_repository" "automation-email-tagger-kre-bridge" {
  name = "automation-email-tagger-kre-bridge"
}

data "external" "email-tagger-kre-bridge-build_number" {
  program = [
    "bash",
    "${path.module}/scripts/obtain_latest_image_for_repository.sh",
    data.aws_ecr_repository.automation-email-tagger-kre-bridge.name
  ]
}

data "template_file" "automation-email-tagger-kre-bridge" {
  template = file("${path.module}/task-definitions/email_tagger_kre_bridge.json")

  vars = {
    image = local.automation-email-tagger-kre-bridge-image
    log_group = var.ENVIRONMENT
    log_prefix = local.log_prefix

    ENVIRONMENT_NAME = var.ENVIRONMENT_NAME
    NATS_SERVER1 = local.nats_server1
    REDIS_HOSTNAME = local.redis-hostname
    KRE_BASE_URL = var.EMAIL_TAGGER_KRE_BRIDGE_KRE_BASE_URL
    PAPERTRAIL_ACTIVE = var.CURRENT_ENVIRONMENT == "production" ? true : false
    PAPERTRAIL_PREFIX = local.automation-email-tagger-kre-bridge-papertrail_prefix
    PAPERTRAIL_HOST = var.PAPERTRAIL_HOST
    PAPERTRAIL_PORT = var.PAPERTRAIL_PORT
    PYTHONUNBUFFERED = var.PYTHONUNBUFFERED
  }
}

resource "aws_ecs_task_definition" "automation-email-tagger-kre-bridge" {
  family = local.automation-email-tagger-kre-bridge-ecs_task_definition-family
  container_definitions = data.template_file.automation-email-tagger-kre-bridge.rendered
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "256"
  memory = "512"
  execution_role_arn = data.aws_iam_role.ecs_execution_role.arn
  task_role_arn = data.aws_iam_role.ecs_execution_role.arn
}

resource "aws_security_group" "automation-email-tagger-kre-bridge_service" {
  vpc_id = data.aws_vpc.mettel-automation-vpc.id
  name = local.automation-email-tagger-kre-bridge-service-security_group-name
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
    Name = local.automation-email-tagger-kre-bridge-service-security_group-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_service_discovery_service" "email-tagger-kre-bridge" {
  name = local.automation-email-tagger-kre-bridge-service_discovery_service-name

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

resource "aws_ecs_service" "automation-email-tagger-kre-bridge" {
  name = local.automation-email-tagger-kre-bridge-resource-name
  task_definition = local.automation-email-tagger-kre-bridge-task_definition
  desired_count = var.email_tagger_kre_bridge_desired_tasks
  launch_type = "FARGATE"
  cluster = aws_ecs_cluster.automation.id
  count = var.email_tagger_kre_bridge_desired_tasks != 0 ? 1 : 0

  network_configuration {
    security_groups = [
      aws_security_group.automation-email-tagger-kre-bridge_service.id]
    subnets = data.aws_subnet_ids.mettel-automation-private-subnets.ids
    assign_public_ip = false
  }

  service_registries {
    registry_arn = aws_service_discovery_service.email-tagger-kre-bridge.arn
  }

  depends_on = [
    null_resource.nats-server-healthcheck,
    aws_elasticache_cluster.automation-redis
  ]
}

data "template_file" "automation-email-tagger-kre-bridge-task-definition-output" {

  template = file("${path.module}/task-definitions/task_definition_output_template.json")

  vars = {
    task_definition_arn = aws_ecs_task_definition.automation-email-tagger-kre-bridge.arn
  }
}

resource "null_resource" "generate_email_tagger_kre_bridge_task_definition_output_json" {
  count = var.email_tagger_kre_bridge_desired_tasks > 0 ? 1 : 0
  provisioner "local-exec" {
    command = format("cat <<\"EOF\" > \"%s\"\n%s\nEOF", var.email-tagger-kre-bridge-task-definition-json, data.template_file.automation-email-tagger-kre-bridge-task-definition-output.rendered)
  }
  triggers = {
    always_run = timestamp()
  }
  depends_on = [aws_ecs_task_definition.automation-email-tagger-kre-bridge]
}

resource "null_resource" "email-tagger-kre-bridge-healthcheck" {
  count = var.email_tagger_kre_bridge_desired_tasks > 0 ? 1 : 0

  depends_on = [aws_ecs_service.automation-email-tagger-kre-bridge,
                aws_ecs_task_definition.automation-email-tagger-kre-bridge,
                null_resource.nats-server-healthcheck,
                null_resource.generate_email_tagger_kre_bridge_task_definition_output_json,
                aws_elasticache_cluster.automation-redis
  ]

  provisioner "local-exec" {
    command = "python3 ci-utils/ecs/task_healthcheck.py -t email-tagger-kre-bridge ${var.email-tagger-kre-bridge-task-definition-json}"
  }

  triggers = {
    always_run = timestamp()
  }
}

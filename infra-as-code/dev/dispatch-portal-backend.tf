locals {
  // automation-dispatch-portal-backend local vars
  automation-dispatch-portal-backend-ecs_task_definition-family = "${var.ENVIRONMENT}-dispatch-portal-backend"
  automation-dispatch-portal-backend-image = "${data.aws_ecr_repository.automation-dispatch-portal-backend.repository_url}:${data.external.dispatch-portal-backend-build_number.result["image_tag"]}"
  automation-dispatch-portal-backend-papertrail_prefix = "dispatch-portal-backend-${element(split("-", data.external.dispatch-portal-backend-build_number.result["image_tag"]),2)}"
  automation-dispatch-portal-backend-service-security_group-name = "${var.ENVIRONMENT}-dispatch-portal-backend"
  automation-dispatch-portal-backend-service-security_group-tag-Name = "${var.ENVIRONMENT}-dispatch-portal-backend"
  automation-dispatch-portal-backend-resource-name = "${var.ENVIRONMENT}-dispatch-portal-backend"
  automation-dispatch-portal-backend-task_definition = "${aws_ecs_task_definition.automation-dispatch-portal-backend.family}:${aws_ecs_task_definition.automation-dispatch-portal-backend.revision}"
  automation-dispatch-portal-backend-service_discovery_service-name = "dispatch-portal-backend-${var.ENVIRONMENT}"
}

data "aws_ecr_repository" "automation-dispatch-portal-backend" {
  name = "automation-dispatch-portal-backend"
}

data "external" "dispatch-portal-backend-build_number" {
  program = [
    "bash",
    "${path.module}/scripts/obtain_latest_image_for_repository.sh",
    data.aws_ecr_repository.automation-dispatch-portal-backend.name
  ]
}

data "template_file" "automation-dispatch-portal-backend" {
  template = file("${path.module}/task-definitions/dispatch_portal_backend.json")

  vars = {
    image = local.automation-dispatch-portal-backend-image
    log_group = var.ENVIRONMENT
    log_prefix = local.log_prefix

    PYTHONUNBUFFERED = var.PYTHONUNBUFFERED
    NATS_SERVER1 = local.nats_server1
    REDIS_HOSTNAME = local.redis-hostname
    DISPATCH_PORTAL_SERVER_PORT = var.DISPATCH_PORTAL_SERVER_PORT
    PAPERTRAIL_ACTIVE = var.CURRENT_ENVIRONMENT == "production" ? true : false
    PAPERTRAIL_PREFIX = local.automation-dispatch-portal-backend-papertrail_prefix
    PAPERTRAIL_HOST = var.PAPERTRAIL_HOST
    PAPERTRAIL_PORT = var.PAPERTRAIL_PORT
    ENVIRONMENT_NAME = var.ENVIRONMENT_NAME
  }
}

resource "aws_ecs_task_definition" "automation-dispatch-portal-backend" {
  family = local.automation-dispatch-portal-backend-ecs_task_definition-family
  container_definitions = data.template_file.automation-dispatch-portal-backend.rendered
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "256"
  memory = "512"
  execution_role_arn = data.aws_iam_role.ecs_execution_role.arn
  task_role_arn = data.aws_iam_role.ecs_execution_role.arn
}

resource "aws_security_group" "automation-dispatch-portal-backend_service" {
  vpc_id = data.aws_vpc.mettel-automation-vpc.id
  name = local.automation-dispatch-portal-backend-service-security_group-name
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
    Name = local.automation-dispatch-portal-backend-service-security_group-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_service_discovery_service" "dispatch-portal-backend" {
  name = local.automation-dispatch-portal-backend-service_discovery_service-name

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

resource "aws_ecs_service" "automation-dispatch-portal-backend" {
  name = local.automation-dispatch-portal-backend-resource-name
  task_definition = local.automation-dispatch-portal-backend-task_definition
  desired_count = var.dispatch_portal_backend_desired_tasks
  launch_type = "FARGATE"
  cluster = aws_ecs_cluster.automation.id
  count = var.dispatch_portal_backend_desired_tasks != 0 ? 1 : 0

  network_configuration {
    security_groups = [
      aws_security_group.automation-dispatch-portal-backend_service.id]
    subnets = data.aws_subnet_ids.mettel-automation-private-subnets.ids
    assign_public_ip = false
  }

  service_registries {
    registry_arn = aws_service_discovery_service.dispatch-portal-backend.arn
  }

  depends_on = [ null_resource.bruin-bridge-healthcheck,
                 null_resource.cts-bridge-healthcheck,
                 null_resource.lit-bridge-healthcheck,
                 null_resource.metrics-prometheus-healthcheck,
                 null_resource.notifier-healthcheck,
                 null_resource.velocloud-bridge-healthcheck,
                 null_resource.t7-bridge-healthcheck]
}

data "template_file" "automation-dispatch-portal-backend-task-definition-output" {

  template = file("${path.module}/task-definitions/task_definition_output_template.json")

  vars = {
    task_definition_arn = aws_ecs_task_definition.automation-dispatch-portal-backend.arn
  }
}

resource "null_resource" "generate_dispatch_portal_backend_task_definition_output_json" {
  count = var.dispatch_portal_backend_desired_tasks > 0 ? 1 : 0
  provisioner "local-exec" {
    command = format("cat <<\"EOF\" > \"%s\"\n%s\nEOF", var.dispatch-portal-backend-task-definition-json, data.template_file.automation-dispatch-portal-backend-task-definition-output.rendered)
  }
  triggers = {
    always_run = timestamp()
  }
  depends_on = [aws_ecs_task_definition.automation-dispatch-portal-backend]
}

resource "null_resource" "dispatch-portal-backend-healthcheck" {
  count = var.dispatch_portal_backend_desired_tasks > 0 ? 1 : 0

  depends_on = [aws_ecs_service.automation-dispatch-portal-backend,
                aws_ecs_task_definition.automation-dispatch-portal-backend,
                null_resource.bruin-bridge-healthcheck,
                null_resource.cts-bridge-healthcheck,
                null_resource.digi-bridge-healthcheck,
                null_resource.email-tagger-kre-bridge-healthcheck,
                null_resource.lit-bridge-healthcheck,
                null_resource.metrics-prometheus-healthcheck,
                null_resource.notifier-healthcheck,
                null_resource.velocloud-bridge-healthcheck,
                null_resource.hawkeye-bridge-healthcheck,
                null_resource.t7-bridge-healthcheck,
                null_resource.generate_dispatch_portal_backend_task_definition_output_json,
                aws_elasticache_cluster.automation-redis
  ]

  provisioner "local-exec" {
    command = "python3 ci-utils/ecs/task_healthcheck.py -t dispatch-portal-backend ${var.dispatch-portal-backend-task-definition-json}"
  }

  triggers = {
    always_run = timestamp()
  }
}

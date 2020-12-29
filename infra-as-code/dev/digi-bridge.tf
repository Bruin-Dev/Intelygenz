data "aws_ecr_repository" "automation-digi-bridge" {
  name = "automation-digi-bridge"
}

data "external" "digi-bridge-build_number" {
  program = [
    "bash",
    "${path.module}/scripts/obtain_latest_image_for_repository.sh",
    data.aws_ecr_repository.automation-digi-bridge.name
  ]
}

data "template_file" "automation-digi-bridge" {
  template = file("${path.module}/task-definitions/digi_bridge.json")

  vars = {
    image = local.automation-digi-bridge-image
    log_group = var.ENVIRONMENT
    log_prefix = local.log_prefix
    DIGI_CLIENT_ID = var.DIGI_CLIENT_ID
    DIGI_CLIENT_SECRET = var.DIGI_CLIENT_SECRET
    DIGI_BASE_URL = var.DIGI_BASE_URL
    DIGI_IP_PRO = var.DIGI_IP_PRO
    DIGI_RECORD_NAME_PRO = var.DIGI_RECORD_NAME_PRO
    DIGI_IP_DEV = var.DIGI_IP_DEV
    DIGI_RECORD_NAME_DEV = var.DIGI_RECORD_NAME_DEV
    DIGI_IP_TEST = var.DIGI_IP_TEST
    DIGI_RECORD_NAME_TEST = var.DIGI_RECORD_NAME_TEST
    NATS_SERVER1 = local.nats_server1
    PYTHONUNBUFFERED = var.PYTHONUNBUFFERED
    REDIS_HOSTNAME = local.redis-hostname
    CURRENT_ENVIRONMENT = var.CURRENT_ENVIRONMENT
    PAPERTRAIL_ACTIVE = var.CURRENT_ENVIRONMENT == "production" ? true : false
    PAPERTRAIL_PREFIX = local.automation-digi-bridge-papertrail_prefix
    PAPERTRAIL_HOST = var.PAPERTRAIL_HOST
    PAPERTRAIL_PORT = var.PAPERTRAIL_PORT
    ENVIRONMENT_NAME = var.ENVIRONMENT_NAME
  }
}

resource "aws_ecs_task_definition" "automation-digi-bridge" {
  family = local.automation-digi-bridge-ecs_task_definition-family
  container_definitions = data.template_file.automation-digi-bridge.rendered
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "1024"
  memory = "2048"
  execution_role_arn = data.aws_iam_role.ecs_execution_role.arn
  task_role_arn = data.aws_iam_role.ecs_execution_role.arn
}

resource "aws_security_group" "automation-digi-bridge_service" {
  vpc_id = data.aws_vpc.mettel-automation-vpc.id
  name = local.automation-digi-bridge_service-security_group-name
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
    Name = local.automation-digi-bridge-service-security_group-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_service_discovery_service" "digi-bridge" {
  name = local.automation-digi-bridge-service_discovery_service-name

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

resource "aws_ecs_service" "automation-digi-bridge" {
  name = local.automation-digi-bridge-resource-name
  task_definition = local.automation-digi-bridge-task_definition
  desired_count = var.digi_bridge_desired_tasks
  launch_type = "FARGATE"
  cluster = aws_ecs_cluster.automation.id
  count = var.digi_bridge_desired_tasks > 0 ? 1 : 0

  network_configuration {
    security_groups = [
      aws_security_group.automation-digi-bridge_service.id]
    subnets = data.aws_subnet_ids.mettel-automation-private-subnets.ids
    assign_public_ip = false
  }

  service_registries {
    registry_arn = aws_service_discovery_service.digi-bridge.arn
  }

  depends_on = [
    null_resource.nats-server-healthcheck,
    aws_elasticache_cluster.automation-redis
  ]
}

data "template_file" "automation-digi-bridge-task-definition-output" {

  template = file("${path.module}/task-definitions/task_definition_output_template.json")

  vars = {
    task_definition_arn = aws_ecs_task_definition.automation-digi-bridge.arn
  }
}

resource "null_resource" "generate_digi_bridge_task_definition_output_json" {
  count = var.digi_bridge_desired_tasks > 0 ? 1 : 0
  provisioner "local-exec" {
    command = format("cat <<\"EOF\" > \"%s\"\n%s\nEOF", var.digi-bridge-task-definition-json, data.template_file.automation-digi-bridge-task-definition-output.rendered)
  }
  triggers = {
    always_run = timestamp()
  }
  depends_on = [aws_ecs_task_definition.automation-digi-bridge]
}

resource "null_resource" "digi-bridge-healthcheck" {
  count = var.digi_bridge_desired_tasks > 0 ? 1 : 0

  depends_on = [aws_ecs_service.automation-digi-bridge,
                aws_ecs_task_definition.automation-digi-bridge,
                null_resource.nats-server-healthcheck,
                null_resource.generate_digi_bridge_task_definition_output_json,
                aws_elasticache_cluster.automation-redis
  ]

  provisioner "local-exec" {
    command = "python3 ci-utils/ecs/task_healthcheck.py -t digi-bridge ${var.digi-bridge-task-definition-json}"
  }

  triggers = {
    always_run = timestamp()
  }
}
data "aws_ecr_repository" "automation-velocloud-bridge" {
  name = "automation-velocloud-bridge"
}

data "external" "velocloud-bridge-build_number" {
  program = [
    "bash",
    "${path.module}/scripts/obtain_latest_image_for_repository.sh",
    data.aws_ecr_repository.automation-velocloud-bridge.name
  ]
}

data "template_file" "automation-velocloud-bridge" {
  template = file("${path.module}/task-definitions/velocloud_bridge.json")

  vars = {
    image = local.automation-velocloud-bridge-image
    log_group = var.ENVIRONMENT
    log_prefix = local.automation-velocloud-bridge-log_prefix

    PYTHONUNBUFFERED = var.PYTHONUNBUFFERED
    NATS_SERVER1 = local.nats_server1
    REDIS_HOSTNAME = local.redis-hostname
    VELOCLOUD_CREDENTIALS = var.VELOCLOUD_CREDENTIALS
    VELOCLOUD_VERIFY_SSL = var.VELOCLOUD_VERIFY_SSL
    REDIS_HOSTNAME = local.redis-hostname
    PAPERTRAIL_ACTIVE = var.CURRENT_ENVIRONMENT == "production" ? true : false
    PAPERTRAIL_PREFIX = local.automation-velocloud-bridge-papertrail_prefix
    PAPERTRAIL_HOST = var.PAPERTRAIL_HOST
    PAPERTRAIL_PORT = var.PAPERTRAIL_PORT
    ENVIRONMENT_NAME = var.ENVIRONMENT_NAME
  }
}

resource "aws_ecs_task_definition" "automation-velocloud-bridge" {
  family = local.automation-velocloud-bridge-ecs_task_definition-family
  container_definitions = data.template_file.automation-velocloud-bridge.rendered
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "2048"
  memory = "4096"
  execution_role_arn = data.aws_iam_role.ecs_execution_role.arn
  task_role_arn = data.aws_iam_role.ecs_execution_role.arn
}

resource "aws_security_group" "automation-velocloud-bridge_service" {
  vpc_id = data.aws_vpc.mettel-automation-vpc.id
  name = "${var.ENVIRONMENT}-velocloud-bridge"
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
    Name = local.automation-velocloud-bridge-service-security_group-tag-Name
    Environment = var.ENVIRONMENT
  }
}
resource "aws_service_discovery_service" "velocloud-bridge" {
  name = local.automation-velocloud-bridge-service_discovery_service-name

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

resource "aws_ecs_service" "automation-velocloud-bridge" {
  name = local.automation-velocloud-bridge-ecs_service-name
  task_definition = local.automation-velocloud-bridge-ecs_service-task_definition
  desired_count = var.velocloud_bridge_desired_tasks
  launch_type = "FARGATE"
  cluster = aws_ecs_cluster.automation.id
  count = var.velocloud_bridge_desired_tasks > 0 ? 1 : 0

  network_configuration {
    security_groups = [
      aws_security_group.automation-velocloud-bridge_service.id]
    subnets = data.aws_subnet_ids.mettel-automation-private-subnets.ids
    assign_public_ip = false
  }

  service_registries {
    registry_arn = aws_service_discovery_service.velocloud-bridge.arn
  }

  depends_on = [ null_resource.nats-server-healthcheck, aws_elasticache_cluster.automation-redis ]
}

data "template_file" "automation-velocloud-bridge-task-definition-output" {
  template = file("${path.module}/task-definitions/task_definition_output_template.json")

  vars = {
    task_definition_arn = aws_ecs_task_definition.automation-velocloud-bridge.arn
  }
}

resource "null_resource" "generate_velocloud_bridge_task_definition_output_json" {
  count = var.velocloud_bridge_desired_tasks > 0 ? 1 : 0
  provisioner "local-exec" {
    command = format("cat <<\"EOF\" > \"%s\"\n%s\nEOF", var.velocloud-bridge-task-definition-json, data.template_file.automation-velocloud-bridge-task-definition-output.rendered)
  }
  triggers = {
    always_run = timestamp()
  }
  depends_on = [aws_ecs_task_definition.automation-velocloud-bridge]
}

resource "null_resource" "velocloud-bridge-healthcheck" {
  count = var.velocloud_bridge_desired_tasks > 0 ? 1 : 0

  depends_on = [aws_ecs_service.automation-velocloud-bridge,
                aws_ecs_task_definition.automation-velocloud-bridge,
                null_resource.nats-server-healthcheck,
                null_resource.generate_velocloud_bridge_task_definition_output_json,
                aws_elasticache_cluster.automation-redis]

  provisioner "local-exec" {
    command = "python3 ci-utils/ecs/task_healthcheck.py -t velocloud-bridge ${var.velocloud-bridge-task-definition-json}"
  }

  triggers = {
    always_run = timestamp()
  }
}

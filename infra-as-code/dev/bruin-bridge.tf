data "aws_ecr_repository" "automation-bruin-bridge" {
  name = "automation-bruin-bridge"
}

data "external" "bruin-bridge-build_number" {
  program = [
    "bash",
    "${path.module}/scripts/obtain_latest_image_for_repository.sh",
    data.aws_ecr_repository.automation-bruin-bridge.name
  ]
}

data "template_file" "automation-bruin-bridge" {
  template = file("${path.module}/task-definitions/bruin_bridge.json")

  vars = {
    image = local.automation-bruin-bridge-image
    log_group = var.ENVIRONMENT
    log_prefix = local.log_prefix
    
    PYTHONUNBUFFERED = var.PYTHONUNBUFFERED
    NATS_SERVER1 = local.nats_server1
    REDIS_HOSTNAME = local.redis-hostname
    BRUIN_CLIENT_ID = var.BRUIN_CLIENT_ID
    BRUIN_CLIENT_SECRET = var.BRUIN_CLIENT_SECRET
    BRUIN_LOGIN_URL = var.BRUIN_LOGIN_URL
    BRUIN_BASE_URL = var.BRUIN_BASE_URL
    PAPERTRAIL_ACTIVE = var.CURRENT_ENVIRONMENT == "production" ? true : false
    PAPERTRAIL_PREFIX = local.automation-bruin-bridge-papertrail_prefix
    PAPERTRAIL_HOST = var.PAPERTRAIL_HOST
    PAPERTRAIL_PORT = var.PAPERTRAIL_PORT
    ENVIRONMENT_NAME = var.ENVIRONMENT_NAME
  }
}

resource "aws_ecs_task_definition" "automation-bruin-bridge" {
  family = local.automation-bruin-bridge-ecs_task_definition-family
  container_definitions = data.template_file.automation-bruin-bridge.rendered
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "1024"
  memory = "2048"
  execution_role_arn = data.aws_iam_role.ecs_execution_role.arn
  task_role_arn = data.aws_iam_role.ecs_execution_role.arn
}

resource "aws_security_group" "automation-bruin-bridge_service" {
  vpc_id = data.aws_vpc.mettel-automation-vpc.id
  name = local.automation-bruin-bridge_service-security_group-name
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
    Name = local.automation-bruin-bridge-service-security_group-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_service_discovery_service" "bruin-bridge" {
  name = local.automation-bruin-bridge-service_discovery_service-name

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

resource "aws_ecs_service" "automation-bruin-bridge" {
  name = local.automation-bruin-bridge-resource-name
  task_definition = local.automation-bruin-bridge-task_definition
  desired_count = var.bruin_bridge_desired_tasks
  launch_type = "FARGATE"
  cluster = aws_ecs_cluster.automation.id
  count = var.bruin_bridge_desired_tasks > 0 ? 1 : 0

  network_configuration {
    security_groups = [
      aws_security_group.automation-bruin-bridge_service.id]
    subnets = data.aws_subnet_ids.mettel-automation-private-subnets.ids
    assign_public_ip = false
  }

  service_registries {
    registry_arn = aws_service_discovery_service.bruin-bridge.arn
  }

  depends_on = [
    null_resource.nats-server-healthcheck,
    aws_elasticache_cluster.automation-redis
  ]
}

data "template_file" "automation-bruin-bridge-task-definition-output" {

  template = file("${path.module}/task-definitions/task_definition_output_template.json")

  vars = {
    task_definition_arn = aws_ecs_task_definition.automation-bruin-bridge.arn
  }
}

resource "null_resource" "generate_bruin_bridge_task_definition_output_json" {
  count = var.bruin_bridge_desired_tasks > 0 ? 1 : 0
  provisioner "local-exec" {
    command = format("cat <<\"EOF\" > \"%s\"\n%s\nEOF", var.bruin-bridge-task-definition-json, data.template_file.automation-bruin-bridge-task-definition-output.rendered)
  }
  triggers = {
    always_run = timestamp()
  }
  depends_on = [aws_ecs_task_definition.automation-bruin-bridge]
}

resource "null_resource" "bruin-bridge-healthcheck" {
  count = var.bruin_bridge_desired_tasks > 0 ? 1 : 0

  depends_on = [aws_ecs_service.automation-bruin-bridge,
                aws_ecs_task_definition.automation-bruin-bridge,
                null_resource.nats-server-healthcheck,
                null_resource.generate_bruin_bridge_task_definition_output_json,
                aws_elasticache_cluster.automation-redis
  ]

  provisioner "local-exec" {
    command = "python3 ci-utils/ecs/task_healthcheck.py -t bruin-bridge ${var.bruin-bridge-task-definition-json}"
  }

  triggers = {
    always_run = timestamp()
  }
}
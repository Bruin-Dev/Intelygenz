data "aws_ecr_repository" "automation-lit-bridge" {
  name = "automation-lit-bridge"
}

data "template_file" "automation-lit-bridge" {
  template = file("${path.module}/task-definitions/lit_bridge.json")

  vars = {
    image = local.automation-lit-bridge-image
    log_group = var.ENVIRONMENT
    log_prefix = local.log_prefix
    
    PYTHONUNBUFFERED = var.PYTHONUNBUFFERED
    NATS_SERVER1 = local.nats_server1
    REDIS_HOSTNAME = local.redis-hostname
    LIT_CLIENT_ID = var.LIT_CLIENT_ID
    LIT_CLIENT_SECRET = var.LIT_CLIENT_SECRET
    LIT_CLIENT_USERNAME = var.LIT_CLIENT_USERNAME
    LIT_CLIENT_PASSWORD = var.LIT_CLIENT_PASSWORD
    LIT_CLIENT_SECURITY_TOKEN = var.LIT_CLIENT_SECURITY_TOKEN
    LIT_LOGIN_URL = var.LIT_LOGIN_URL
    LIT_DOMAIN = var.LIT_DOMAIN
    PAPERTRAIL_ACTIVE = var.CURRENT_ENVIRONMENT == "dev" ? true : false
    PAPERTRAIL_PREFIX = local.automation-lit-bridge-papertrail_prefix
    PAPERTRAIL_HOST = var.PAPERTRAIL_HOST
    PAPERTRAIL_PORT = var.PAPERTRAIL_PORT
    ENVIRONMENT_NAME = var.ENVIRONMENT_NAME
  }
}

resource "aws_ecs_task_definition" "automation-lit-bridge" {
  family = local.automation-lit-bridge-ecs_task_definition-family
  container_definitions = data.template_file.automation-lit-bridge.rendered
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "1024"
  memory = "2048"
  execution_role_arn = data.aws_iam_role.ecs_execution_role.arn
  task_role_arn = data.aws_iam_role.ecs_execution_role.arn
}

resource "aws_security_group" "automation-lit-bridge_service" {
  vpc_id = data.terraform_remote_state.tfstate-network-resources.outputs.vpc_automation_id
  name = local.automation-lit-bridge_service-security_group-name
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

  ingress {
    from_port = 9090
    to_port = 9090
    protocol = "TCP"
    cidr_blocks = [
      var.cidr_base[var.CURRENT_ENVIRONMENT]
    ]
  }

  tags = {
    Name = local.automation-lit-bridge-service-security_group-tag-Name
    Environment = var.ENVIRONMENT
  }
}
resource "aws_service_discovery_service" "lit-bridge" {
  name = local.automation-lit-bridge-service_discovery_service-name

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

resource "aws_ecs_service" "automation-lit-bridge" {
  name = local.automation-lit-bridge-resource-name
  task_definition = local.automation-lit-bridge-task_definition
  desired_count = var.lit_bridge_desired_tasks
  launch_type = "FARGATE"
  cluster = aws_ecs_cluster.automation.id
  count = var.lit_bridge_desired_tasks > 0 ? 1 : 0

  network_configuration {
    security_groups = [
      aws_security_group.automation-lit-bridge_service.id]
    subnets = [
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1a.id,
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1b.id]
    assign_public_ip = false
  }

  service_registries {
    registry_arn = aws_service_discovery_service.lit-bridge.arn
  }

  depends_on = [
    null_resource.nats-server-healthcheck,
    aws_elasticache_cluster.automation-redis
  ]
}

data "template_file" "automation-lit-bridge-task-definition-output" {

  template = file("${path.module}/task-definitions/task_definition_output_template.json")

  vars = {
    task_definition_arn = aws_ecs_task_definition.automation-lit-bridge.arn
  }
}

resource "null_resource" "generate_lit_bridge_task_definition_output_json" {
  count = var.lit_bridge_desired_tasks > 0 ? 1 : 0
  provisioner "local-exec" {
    command = format("cat <<\"EOF\" > \"%s\"\n%s\nEOF", var.lit-bridge-task-definition-json, data.template_file.automation-lit-bridge-task-definition-output.rendered)
  }
  triggers = {
    always_run = timestamp()
  }
  depends_on = [aws_ecs_task_definition.automation-lit-bridge]
}

resource "null_resource" "lit-bridge-healthcheck" {
  count = var.lit_bridge_desired_tasks > 0 ? 1 : 0

  depends_on = [aws_ecs_service.automation-lit-bridge,
                aws_ecs_task_definition.automation-lit-bridge,
                null_resource.nats-server-healthcheck,
                null_resource.generate_lit_bridge_task_definition_output_json,
                aws_elasticache_cluster.automation-redis
  ]

  provisioner "local-exec" {
    command = "python3 ci-utils/ecs/task_healthcheck.py -t lit-bridge ${var.lit-bridge-task-definition-json}"
  }

  triggers = {
    always_run = timestamp()
  }
}
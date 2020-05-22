data "aws_ecr_repository" "automation-cts-bridge" {
  name = "automation-cts-bridge"
}

data "template_file" "automation-cts-bridge" {
  template = file("${path.module}/task-definitions/cts_bridge.json")

  vars = {
    image = local.automation-cts-bridge-image
    log_group = var.ENVIRONMENT
    log_prefix = local.log_prefix

    CTS_CLIENT_ID = var.CTS_CLIENT_ID
    CTS_CLIENT_SECRET = var.CTS_CLIENT_SECRET
    CTS_CLIENT_USERNAME = var.CTS_CLIENT_USERNAME
    CTS_CLIENT_PASSWORD = var.CTS_CLIENT_PASSWORD
    CTS_CLIENT_SECURITY_TOKEN = var.CTS_CLIENT_SECURITY_TOKEN
    CTS_LOGIN_URL = var.CTS_LOGIN_URL
    CTS_DOMAIN = var.CTS_DOMAIN
    NATS_SERVER1 = local.nats_server1
    PYTHONUNBUFFERED = var.PYTHONUNBUFFERED
    REDIS_HOSTNAME = local.redis-hostname
  }
}

resource "aws_ecs_task_definition" "automation-cts-bridge" {
  family = local.automation-cts-bridge-ecs_task_definition-family
  container_definitions = data.template_file.automation-cts-bridge.rendered
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "1024"
  memory = "2048"
  execution_role_arn = data.aws_iam_role.ecs_execution_role.arn
  task_role_arn = data.aws_iam_role.ecs_execution_role.arn
}

resource "aws_security_group" "automation-cts-bridge_service" {
  vpc_id = data.terraform_remote_state.tfstate-network-resources.outputs.vpc_automation_id
  name = local.automation-cts-bridge_service-security_group-name
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
    Name = local.automation-cts-bridge-service-security_group-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_service_discovery_service" "cts-bridge" {
  name = local.automation-cts-bridge-service_discovery_service-name

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

resource "aws_ecs_service" "automation-cts-bridge" {
  name = local.automation-cts-bridge-resource-name
  task_definition = local.automation-cts-bridge-task_definition
  desired_count = var.cts_bridge_desired_tasks
  launch_type = "FARGATE"
  cluster = aws_ecs_cluster.automation.id
  count = var.cts_bridge_desired_tasks > 0 ? 1 : 0

  network_configuration {
    security_groups = [
      aws_security_group.automation-cts-bridge_service.id]
    subnets = [
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1a.id,
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1b.id]
    assign_public_ip = false
  }

  service_registries {
    registry_arn = aws_service_discovery_service.cts-bridge.arn
  }

  depends_on = [
    null_resource.nats-server-healthcheck,
    aws_elasticache_cluster.automation-redis
  ]
}

data "template_file" "automation-cts-bridge-task-definition-output" {

  template = file("${path.module}/task-definitions/task_definition_output_template.json")

  vars = {
    task_definition_arn = aws_ecs_task_definition.automation-cts-bridge.arn
  }
}

resource "null_resource" "generate_cts_bridge_task_definition_output_json" {
  count = var.cts_bridge_desired_tasks > 0 ? 1 : 0
  provisioner "local-exec" {
    command = format("cat <<\"EOF\" > \"%s\"\n%s\nEOF", var.cts-bridge-task-definition-json, data.template_file.automation-cts-bridge-task-definition-output.rendered)
  }
  triggers = {
    always_run = timestamp()
  }
  depends_on = [aws_ecs_task_definition.automation-cts-bridge]
}

resource "null_resource" "cts-bridge-healthcheck" {
  count = var.cts_bridge_desired_tasks > 0 ? 1 : 0

  depends_on = [aws_ecs_service.automation-cts-bridge,
                aws_ecs_task_definition.automation-cts-bridge,
                null_resource.nats-server-healthcheck,
                null_resource.generate_cts_bridge_task_definition_output_json,
                aws_elasticache_cluster.automation-redis
  ]

  provisioner "local-exec" {
    command = "python3 ci-utils/task_healthcheck.py -t cts-bridge ${var.cts-bridge-task-definition-json}"
  }

  triggers = {
    always_run = timestamp()
  }
}
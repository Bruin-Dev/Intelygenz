data "aws_ecr_repository" "automation-bruin-bridge" {
  name = "automation-bruin-bridge"
}

data "template_file" "automation-bruin-bridge" {
  template = file("${path.module}/task-definitions/bruin_bridge.json")

  vars = {
    image = local.automation-bruin-bridge-image
    log_group = var.ENVIRONMENT
    log_prefix = local.log_prefix
    
    PYTHONUNBUFFERED = var.PYTHONUNBUFFERED
    NATS_SERVER1 = local.nats_server1
    BRUIN_CLIENT_ID = var.BRUIN_CLIENT_ID
    BRUIN_CLIENT_SECRET = var.BRUIN_CLIENT_SECRET
    BRUIN_LOGIN_URL = var.BRUIN_LOGIN_URL
    BRUIN_BASE_URL = var.BRUIN_BASE_URL
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
  vpc_id = data.terraform_remote_state.tfstate-network-resources.outputs.vpc_automation_id
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

  ingress {
    from_port = 9090
    to_port = 9090
    protocol = "TCP"
    cidr_blocks = [
      var.cidr_base[var.CURRENT_ENVIRONMENT]
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
    subnets = [
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1a.id,
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1b.id]
    assign_public_ip = false
  }

  service_registries {
    registry_arn = aws_service_discovery_service.bruin-bridge.arn
  }

  depends_on = [ null_resource.nats-server-healthcheck ]
}

resource "null_resource" "bruin-bridge-healthcheck" {
  count = var.bruin_bridge_desired_tasks > 0 ? 1 : 0

  depends_on = [aws_ecs_service.automation-bruin-bridge]

  provisioner "local-exec" {
    command = "python3 ci-utils/task_healthcheck.py -t bruin-bridge"
  }

  triggers = {
    always_run = timestamp()
  }
}
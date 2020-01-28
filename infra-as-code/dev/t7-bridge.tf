data "aws_ecr_repository" "automation-t7-bridge" {
  name = "automation-t7-bridge"
}

data "template_file" "automation-t7-bridge" {
  template = file("${path.module}/task-definitions/t7_bridge.json")

  vars = {
    image = local.automation-t7-bridge-image
    log_group = var.ENVIRONMENT
    log_prefix = local.log_prefix

    PYTHONUNBUFFERED = var.PYTHONUNBUFFERED
    NATS_SERVER1 = local.nats_server1
    REDIS_HOSTNAME = local.redis-hostname
    T7_BASE_URL = var.T7_BASE_URL
    T7_TOKEN = var.T7_TOKEN

  }
}

resource "aws_ecs_task_definition" "automation-t7-bridge" {
  family = "${var.ENVIRONMENT}-t7-bridge"
  container_definitions = data.template_file.automation-t7-bridge.rendered
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "256"
  memory = "512"
  execution_role_arn = data.aws_iam_role.ecs_execution_role.arn
  task_role_arn = data.aws_iam_role.ecs_execution_role.arn
}

resource "aws_security_group" "automation-t7-bridge_service" {
  vpc_id = data.terraform_remote_state.tfstate-network-resources.outputs.vpc_automation_id
  name = local.automation-t7-bridge_service-security_group-name
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
    Name = local.automation-t7-bridge-service-security_group-tag-Name
    Environment = var.ENVIRONMENT
  }
}
resource "aws_service_discovery_service" "t7-bridge" {
  name = local.automation-t7-bridge-service_discovery_service-name

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

resource "aws_ecs_service" "automation-t7-bridge" {
  name = local.automation-t7-bridge-resource-name
  task_definition = local.automation-t7-bridge-task_definition
  desired_count = var.t7_bridge_desired_tasks
  launch_type = "FARGATE"
  cluster = aws_ecs_cluster.automation.id
  count = var.t7_bridge_desired_tasks > 0 ? 1 : 0

  network_configuration {
    security_groups = [
      aws_security_group.automation-t7-bridge_service.id]
    subnets = [
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1a.id,
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1b.id]
    assign_public_ip = false
  }

  service_registries {
    registry_arn = aws_service_discovery_service.t7-bridge.arn
  }

  depends_on = [ null_resource.nats-server-healthcheck ]
}

data "template_file" "automation-t7-bridge-task-definition-output" {
  template = file("${path.module}/task-definitions/task_definition_output_template.json")

  vars = {
    task_definition_arn = aws_ecs_task_definition.automation-t7-bridge.arn
  }
}

resource "null_resource" "generate_t7_bridge_task_definition_output_json" {
  count = var.t7_bridge_desired_tasks > 0 ? 1 : 0
  provisioner "local-exec" {
    command = format("cat <<\"EOF\" > \"%s\"\n%s\nEOF", var.t7-bridge-task-definition-json, data.template_file.automation-t7-bridge-task-definition-output.rendered)
  }
  triggers = {
    always_run = timestamp()
  }
  depends_on = [aws_ecs_task_definition.automation-t7-bridge]
}

resource "null_resource" "t7-bridge-healthcheck" {
  count = var.t7_bridge_desired_tasks > 0 ? 1 : 0

  depends_on = [aws_ecs_service.automation-t7-bridge,
                aws_ecs_task_definition.automation-t7-bridge,
                null_resource.nats-server-healthcheck,
                null_resource.generate_t7_bridge_task_definition_output_json]

  provisioner "local-exec" {
    command = "python3 ci-utils/task_healthcheck.py -t t7-bridge ${var.t7-bridge-task-definition-json}"
  }

  triggers = {
    always_run = timestamp()
  }
}

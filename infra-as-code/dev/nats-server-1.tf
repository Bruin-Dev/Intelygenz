data "template_file" "automation-nats-server-1" {
  template = file("${path.module}/task-definitions/nats_server.json")

  vars = {
    image = local.automation-nats-server-1-image
    log_group = var.ENVIRONMENT
    log_prefix = local.log_prefix

    CONTAINER_NAME = local.automation-nats-server-1-task_definition_template-container_name
    NATSCLUSTER =  local.automation-nats-server-1-task_definition_template-natscluster
    NATSCLUSTERPORT = var.NATS_SERVER_1_CLIENTS_PORT
    NATSROUTECLUSTER = local.automation-nats-server-1-task_definition_template-natsroutecluster
    PORT = var.NATS_SERVER_1_CLIENTS_PORT
    CLUSTER_MODE = var.NATS_SERVER_1_CLUSTER_MODE
  }
}

resource "aws_ecs_task_definition" "automation-nats-server-1" {
  family = local.automation-nats-server-1-ecs_task_definition-family
  container_definitions = data.template_file.automation-nats-server-1.rendered
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "256"
  memory = "1024"
  execution_role_arn = data.aws_iam_role.ecs_execution_role.arn
  task_role_arn = data.aws_iam_role.ecs_execution_role.arn
}

resource "aws_security_group" "automation-nats_service-1" {
  vpc_id = data.terraform_remote_state.tfstate-network-resources.outputs.vpc_automation_id
  name = local.automation-nats-server-1-nats_service-security_group-name
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
    from_port = 8222
    to_port = 8222
    protocol = "TCP"
    cidr_blocks = [
      "0.0.0.0/0"
    ]
  }

  ingress {
    from_port = 4222
    to_port = 4222
    protocol = "TCP"
    cidr_blocks = [
      var.cidr_base[var.CURRENT_ENVIRONMENT]
    ]
  }

  ingress {
    from_port = var.NATS_SERVER_1_CLUSTER_PORT
    to_port = var.NATS_SERVER_1_CLUSTER_PORT
    protocol = "TCP"
    cidr_blocks = [
      var.cidr_base[var.CURRENT_ENVIRONMENT]
    ]
  }

  tags = {
    Name = local.automation-nats-server-1-nats_service-security_group-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_service_discovery_service" "nats-server-1" {
  name = "nats-server-1-${var.ENVIRONMENT}"

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

resource "aws_ecs_service" "automation-nats-server-1" {
  name = "${var.ENVIRONMENT}-nats-server-1"
  task_definition = local.automation-nats-server-1-ecs_service-task_definition
  desired_count = var.nats_server_1_desired_tasks
  launch_type = "FARGATE"
  cluster = aws_ecs_cluster.automation.id
  count = var.nats_server_1_desired_tasks != 0 ? 1 : 0

  network_configuration {
    security_groups = [
      aws_security_group.automation-nats_service-1.id]
    subnets = [
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1a.id,
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1b.id]
    assign_public_ip = false
  }

  service_registries {
    registry_arn = aws_service_discovery_service.nats-server-1.arn
  }

  depends_on = [ null_resource.nats-server-healthcheck ]
}

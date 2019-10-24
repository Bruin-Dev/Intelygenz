data "aws_ecr_repository" "automation-service-outage-monitor" {
  name = "automation-service-outage-monitor"
}

data "template_file" "automation-service-outage-monitor" {
  template = file("${path.module}/task-definitions/service_outage_monitor.json")

  vars = {
    image = local.automation-service-outage-monitor-image
    log_group = var.ENVIRONMENT
    log_prefix = local.log_prefix

    PYTHONUNBUFFERED = var.PYTHONUNBUFFERED
    NATS_SERVER1 = local.nats_server1
    CURRENT_ENVIRONMENT = var.CURRENT_ENVIRONMENT
    LAST_CONTACT_RECIPIENT = var.LAST_CONTACT_RECIPIENT

  }
}

resource "aws_ecs_task_definition" "automation-service-outage-monitor" {
  family = local.automation-service-outage-monitor-ecs_task_definition-family
  container_definitions = data.template_file.automation-service-outage-monitor.rendered
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "256"
  memory = "512"
  execution_role_arn = data.terraform_remote_state.tfstate-dev-resources.outputs.ecs_execution_role
  task_role_arn = data.terraform_remote_state.tfstate-dev-resources.outputs.ecs_execution_role
}

resource "aws_security_group" "automation-service-outage-monitor_service" {
  vpc_id = data.terraform_remote_state.tfstate-network-resources.outputs.vpc_automation_id
  name = local.automation-service-outage-monitor-service-security_group-name
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
    Name = local.automation-service-outage-monitor-service-security_group-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_service_discovery_service" "service-outage-monitor" {
  name = local.automation-service-outage-monitor-service_discovery_service-name

  dns_config {
    namespace_id = data.terraform_remote_state.tfstate-dev-resources.outputs.aws_service_discovery_automation-zone_id

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

resource "aws_ecs_service" "automation-service-outage-monitor" {
  name = local.automation-service-outage-monitor-ecs_service-name
  task_definition = local.automation-service-outage-monitor-ecs_service-task_definition
  desired_count = 1
  launch_type = "FARGATE"
  cluster = data.terraform_remote_state.tfstate-dev-resources.outputs.automation_cluster_id

  network_configuration {
    security_groups = [
      aws_security_group.automation-service-outage-monitor_service.id]
    subnets = [
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1a.id,
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1b.id]
    assign_public_ip = false
  }

  service_registries {
    registry_arn = aws_service_discovery_service.service-outage-monitor.arn
  }
}

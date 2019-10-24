data "aws_ecr_repository" "automation-last-contact-report" {
  name = "automation-last-contact-report"
}

data "template_file" "automation-last-contact-report" {
  template = file("${path.module}/task-definitions/last_contact_report.json")

  vars = {
    image = local.automation-last-contact-report-image
    log_group = var.ENVIRONMENT
    log_prefix = local.log_prefix

    PYTHONUNBUFFERED = var.PYTHONUNBUFFERED
    NATS_SERVER1 = local.nats_server1
    LAST_CONTACT_RECIPIENT = var.LAST_CONTACT_RECIPIENT
  }
}

resource "aws_ecs_task_definition" "automation-last-contact-report" {
  family = local.automation-last-contact-report-ecs_task_definition-family
  container_definitions = data.template_file.automation-last-contact-report.rendered
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "256"
  memory = "512"
  execution_role_arn = data.terraform_remote_state.tfstate-dev-resources.outputs.ecs_execution_role
  task_role_arn = data.terraform_remote_state.tfstate-dev-resources.outputs.ecs_execution_role
}

resource "aws_security_group" "automation-last-contact-report_service" {
  vpc_id = data.terraform_remote_state.tfstate-network-resources.outputs.vpc_automation_id
  name = local.automation-last-contact-report-service-security_group-name
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
    Name = local.automation-last-contact-report-service-security_group-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_service_discovery_service" "last-contact-report" {
  name = local.automation-last-contact-service_discovery_service-name

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

resource "aws_ecs_service" "automation-last-contact-report" {
  name = local.automation-last-contact-report-resource-name
  task_definition = local.automation-last-contact-report-task_definition
  desired_count = 1
  launch_type = "FARGATE"
  cluster = data.terraform_remote_state.tfstate-dev-resources.outputs.automation_cluster_id

  network_configuration {
    security_groups = [
      aws_security_group.automation-last-contact-report_service.id]
    subnets = [
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1a.id,
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1b.id]
    assign_public_ip = false
  }

  service_registries {
    registry_arn = aws_service_discovery_service.last-contact-report.arn
  }
}

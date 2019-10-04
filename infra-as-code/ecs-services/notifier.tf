data "aws_ecr_repository" "automation-notifier" {
  name = "automation-notifier"
}

data "template_file" "automation-notifier" {
  template = file("${path.module}/task-definitions/notifier.json")

  vars = {
    image = local.automation-notifier-image
    log_group = var.ENVIRONMENT
    log_prefix = local.log_prefix

    PYTHONUNBUFFERED = var.PYTHONUNBUFFERED
    NATS_SERVER1 = local.nats_server1
    NATS_CLUSTER_NAME = var.NATS_CLUSTER_NAME
    SLACK_URL = local.slack_url
    EMAIL_ACC_PWD = var.EMAIL_ACC_PWD

  }
}

resource "aws_ecs_task_definition" "automation-notifier" {
  family = local.automation-notifier-ecs_task_definition-family
  container_definitions = data.template_file.automation-notifier.rendered
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "256"
  memory = "512"
  execution_role_arn = data.terraform_remote_state.tfstate-dev-resources.outputs.ecs_execution_role
  task_role_arn = data.terraform_remote_state.tfstate-dev-resources.outputs.ecs_execution_role
}

resource "aws_security_group" "automation-notifier_service" {
  vpc_id = data.terraform_remote_state.tfstate-network-resources.outputs.vpc_automation_id
  name = local.automation-notifier-service-security_group-name
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
    Name = local.automation-notifier-service-security_group-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_ecs_service" "automation-notifier" {
  name = local.automation-notifier-ecs_service-name
  task_definition = local.automation-notifier-ecs_service-task_definition
  desired_count = 1
  launch_type = "FARGATE"
  cluster = data.terraform_remote_state.tfstate-dev-resources.outputs.automation_cluster_id

  network_configuration {
    security_groups = [
      aws_security_group.automation-notifier_service.id]
    subnets = [
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1a,
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1b]
    assign_public_ip = false
  }
}

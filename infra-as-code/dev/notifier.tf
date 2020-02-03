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
    SLACK_URL = var.SLACK_URL
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
  execution_role_arn = data.aws_iam_role.ecs_execution_role.arn
  task_role_arn = data.aws_iam_role.ecs_execution_role.arn
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
  desired_count = var.notifier_desired_tasks
  launch_type = "FARGATE"
  cluster = aws_ecs_cluster.automation.id
  count = var.notifier_desired_tasks > 0 ? 1 : 0

  network_configuration {
    security_groups = [
      aws_security_group.automation-notifier_service.id]
    subnets = [
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1a.id,
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1b.id]
    assign_public_ip = false
  }

  depends_on = [ null_resource.nats-server-healthcheck ]
}

data "template_file" "automation-notifier-task-definition-output" {
  template = file("${path.module}/task-definitions/task_definition_output_template.json")

  vars = {
    task_definition_arn = aws_ecs_task_definition.automation-notifier.arn
  }
}

resource "null_resource" "generate_notifier_task_definition_output_json" {
  provisioner "local-exec" {
    command = format("cat <<\"EOF\" > \"%s\"\n%s\nEOF", var.notifier-task-definition-json, data.template_file.automation-notifier-task-definition-output.rendered)
  }
  triggers = {
    always_run = timestamp()
  }
  depends_on = [aws_ecs_task_definition.automation-notifier]
}

resource "null_resource" "notifier-healthcheck" {
  count = var.notifier_desired_tasks > 0 ? 1 : 0

  depends_on = [aws_ecs_service.automation-notifier,
                aws_ecs_task_definition.automation-notifier,
                null_resource.nats-server-healthcheck,
                null_resource.generate_notifier_task_definition_output_json]

  provisioner "local-exec" {
    command = "python3 ci-utils/task_healthcheck.py -t notifier ${var.notifier-task-definition-json}"
  }

  triggers = {
    always_run = timestamp()
  }
}

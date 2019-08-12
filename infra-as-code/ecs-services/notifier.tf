data "aws_ecr_repository" "automation-notifier" {
  name = "automation-notifier"
}

data "template_file" "automation-notifier" {
  template = "${file("${path.module}/task-definitions/notifier.json")}"

  vars = {
    image = "${data.aws_ecr_repository.automation-notifier.repository_url}:${var.BUILD_NUMBER}"
    log_group = "${var.ENVIRONMENT}"
    log_prefix = "${var.ENVIRONMENT}-${var.BUILD_NUMBER}"

    PYTHONUNBUFFERED = "${var.PYTHONUNBUFFERED}"
    NATS_SERVER1 = "nats://nats-server.${var.ENVIRONMENT}.local:4222"
    NATS_CLUSTER_NAME = "${var.NATS_CLUSTER_NAME}"
    SLACK_URL = "https://hooks.slack.com/services/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"
    EMAIL_ACC_PWD = "${var.EMAIL_ACC_PWD}"

  }
}

resource "aws_ecs_task_definition" "automation-notifier" {
  family = "${var.ENVIRONMENT}-notifier"
  container_definitions = "${data.template_file.automation-notifier.rendered}"
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "256"
  memory = "512"
  execution_role_arn = "${data.terraform_remote_state.tfstate-dev-resources.ecs_execution_role}"
  task_role_arn = "${data.terraform_remote_state.tfstate-dev-resources.ecs_execution_role}"
}

resource "aws_security_group" "automation-notifier_service" {
  vpc_id = "${data.terraform_remote_state.tfstate-dev-resources.vpc_automation_id}"
  name = "${var.ENVIRONMENT}-notifier"
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
    Name = "${var.ENVIRONMENT}-notifier"
    Environment = "${var.ENVIRONMENT}"
  }
}

resource "aws_ecs_service" "automation-notifier" {
  name = "${var.ENVIRONMENT}-notifier"
  task_definition = "${aws_ecs_task_definition.automation-notifier.family}:${aws_ecs_task_definition.automation-notifier.revision}"
  desired_count = 1
  launch_type = "FARGATE"
  cluster = "${data.terraform_remote_state.tfstate-dev-resources.automation_cluster_id}"

  network_configuration {
    security_groups = [
      "${aws_security_group.automation-notifier_service.id}"]
    subnets = [
      "${data.terraform_remote_state.tfstate-dev-resources.subnet_automation-private-1a}"]
    assign_public_ip = false
  }
}

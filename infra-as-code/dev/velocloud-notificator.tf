data "aws_ecr_repository" "automation-velocloud-notificator" {
  name = "automation-velocloud-notificator"
}

data "template_file" "automation-velocloud-notificator" {
  template = "${file("${path.module}/task-definitions/velocloud_notificator.json")}"

  vars = {
    image = "${data.aws_ecr_repository.automation-velocloud-notificator.repository_url}:${var.BUILD_NUMBER}"
    log_group = "${var.environment}"
    log_prefix = "${var.environment}-${var.BUILD_NUMBER}"

    PYTHONUNBUFFERED = "${var.PYTHONUNBUFFERED}"
    NATS_SERVER1 = "nats://nats-server.${var.environment}.local:4222"
    NATS_CLUSTER_NAME = "${var.NATS_CLUSTER_NAME}"
    SLACK_URL = "https://hooks.slack.com/services/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"
    EMAIL_ACC_PWD = "${var.EMAIL_ACC_PWD}"

  }
}

resource "aws_ecs_task_definition" "automation-velocloud-notificator" {
  family = "${var.environment}-velocloud-notificator"
  container_definitions = "${data.template_file.automation-velocloud-notificator.rendered}"
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "256"
  memory = "512"
  execution_role_arn = "${aws_iam_role.ecs_execution_role.arn}"
  task_role_arn = "${aws_iam_role.ecs_execution_role.arn}"
}

resource "aws_security_group" "automation-velocloud-notificator_service" {
  vpc_id = "${aws_vpc.automation-vpc.id}"
  name = "${var.environment}-velocloud-notificator"
  description = "Allow egress from container"

  lifecycle {
    create_before_destroy = true
  }

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
    Name = "${var.environment}-velocloud-notificator"
    Environment = "${var.environment}"
  }
}

resource "aws_ecs_service" "automation-velocloud-notificator" {
  name = "${var.environment}-velocloud-notificator"
  task_definition = "${aws_ecs_task_definition.automation-velocloud-notificator.family}:${aws_ecs_task_definition.automation-velocloud-notificator.revision}"
  desired_count = 1
  launch_type = "FARGATE"
  cluster = "${aws_ecs_cluster.automation.id}"

  network_configuration {
    security_groups = [
      "${aws_security_group.automation-velocloud-notificator_service.id}"]
    subnets = [
      "${aws_subnet.automation-private_subnet-1a.id}",
      "${aws_subnet.automation-private_subnet-1b.id}"]
    assign_public_ip = false
  }
}

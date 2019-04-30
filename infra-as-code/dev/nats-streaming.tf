resource "aws_ecr_repository" "automation-nats-streaming-server" {
  name = "${var.environment}-nats-streaming-server"
}

data "template_file" "automation-nats-streaming-server" {
  template = "${file("${path.module}/task-definitions/nats_streaming.json")}"

  vars {
    image = "${aws_ecr_repository.automation-nats-streaming-server.repository_url}:${var.build_number}"
  }
}

resource "aws_ecs_task_definition" "automation-nats-streaming-server" {
  family = "${var.environment}-nats-streaming-server"
  container_definitions = "${data.template_file.automation-nats-streaming-server.rendered}"
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "256"
  memory = "1024"
  execution_role_arn = "${aws_iam_role.ecs_execution_role.arn}"
  task_role_arn = "${aws_iam_role.ecs_execution_role.arn}"
}

resource "aws_alb_target_group" "automation-nats-streaming-server" {
  name = "${var.environment}-nats-streaming-server"
  port = 8222
  protocol = "HTTP"
  vpc_id = "${aws_vpc.automation-vpc.id}"
  target_type = "ip"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group" "automation-nats-streaming_service" {
  vpc_id = "${aws_vpc.automation-vpc.id}"
  name = "${var.environment}-nats-streaming-server"
  description = "Allow egress from container"

  #  egress {
  #    from_port = 0
  #    to_port = 0
  #    protocol = "-1"
  #    cidr_blocks = [
  #      "0.0.0.0/0"]
  #  }

  ingress {
    from_port = 8222
    to_port = 8222
    protocol = "TCP"
    cidr_blocks = [
      "0.0.0.0/0"
    ]
  }

  tags {
    Name = "${var.environment}-nats-streaming-server"
    Environment = "${var.environment}"
  }
}

resource "aws_ecs_service" "automation-nats-streaming-server" {
  name = "${var.environment}-nats-streaming-server"
  task_definition = "${aws_ecs_task_definition.automation-nats-streaming-server.family}:${aws_ecs_task_definition.automation-nats-streaming-server.revision}"
  desired_count = 1
  launch_type = "FARGATE"
  cluster = "${aws_ecs_cluster.automation.id}"

  network_configuration {
    security_groups = [
      "${aws_security_group.automation-nats-streaming_service.id}"]
    subnets = [
      "${aws_subnet.automation-private_subnet-1a.id}",
      "${aws_subnet.automation-private_subnet-1b.id}"]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = "${aws_alb_target_group.automation-nats-streaming-server.arn}"
    container_name = "nats-streaming"
    container_port = 8222
  }
}

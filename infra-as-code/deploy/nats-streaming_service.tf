resource "aws_alb_target_group" "mettel-automation-pro-nats-streaming" {
  name = "${var.environment}-nats-streaming"
  port = 4222
  protocol = "HTTP"
  vpc_id = "${aws_vpc.mettel-automation-pro-vpc.id}"
  target_type = "ip"

#   health_check {
#     path = "/_health"
#   }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group" "mettel-automation-pro-nats-streaming_service" {
  vpc_id = "${aws_vpc.mettel-automation-pro-vpc.id}"
  name = "${var.environment}-nats-streaming"
  description = "Allow egress from container"

#  egress {
#    from_port = 0
#    to_port = 0
#    protocol = "-1"
#    cidr_blocks = [
#      "0.0.0.0/0"]
#  }

  ingress {
    from_port = 8
    to_port = 0
    protocol = "icmp"
    cidr_blocks = [
      "0.0.0.0/0"]
  }

  ingress {
    from_port = 80
    to_port = 80
    protocol = "TCP"
    cidr_blocks = [
      "0.0.0.0/0"
    ]
  }

  tags {
    Name = "${var.environment}-nats-streaming"
    Environment = "${var.environment}"
  }
}

resource "aws_ecs_service" "mettel-automation-pro-nats-streaming" {
  name = "${var.environment}-nats-streaming"
  task_definition = "${aws_ecs_task_definition.mettel-automation-pro-nats-streaming.family}:${aws_ecs_task_definition.mettel-automation-pro-nats-streaming.revision}"
  desired_count = 1
  launch_type = "FARGATE"
  cluster = "${aws_ecs_cluster.mettel-automation-pro.id}"

  network_configuration {
    security_groups = [
      "${aws_security_group.mettel-automation-pro-nats-streaming_service.id}"]
    subnets = [
      "${aws_subnet.mettel-automation-pro-private_subnet-1a.id}",
      "${aws_subnet.mettel-automation-pro-private_subnet-1b.id}"]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = "${aws_alb_target_group.mettel-automation-pro-nats-streaming.arn}"
    container_name = "nats-streaming"
    container_port = 4222
  }
}

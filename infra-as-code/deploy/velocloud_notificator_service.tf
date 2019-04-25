resource "aws_alb_target_group" "mettel-automation-pro-backend" {
  name = "${var.environment}-backend"
  port = 80
  protocol = "HTTP"
  vpc_id = "${aws_vpc.mettel-automation-pro-vpc.id}"
  target_type = "ip"

  health_check {
    path = "/api/health"
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group" "mettel-automation-pro-backend_service" {
  vpc_id = "${aws_vpc.mettel-automation-pro-vpc.id}"
  name = "${var.environment}-backend"
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
    Name = "${var.environment}-backend"
    Environment = "${var.environment}"
  }
}

resource "aws_ecs_service" "mettel-automation-pro-backend" {
  name = "${var.environment}-backend"
  task_definition = "${aws_ecs_task_definition.mettel-automation-pro-backend.family}:${aws_ecs_task_definition.mettel-automation-pro-backend.revision}"
  desired_count = 1
  launch_type = "FARGATE"
  cluster = "${aws_ecs_cluster.mettel-automation-pro.id}"

  network_configuration {
    security_groups = [
      "${aws_security_group.mettel-automation-pro-backend_service.id}"]
    subnets = [
      "${aws_subnet.mettel-automation-pro-private_subnet-1a.id}",
      "${aws_subnet.mettel-automation-pro-private_subnet-1b.id}"]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = "${aws_alb_target_group.mettel-automation-pro-backend.arn}"
    container_name = "backend"
    container_port = 80
  }
}

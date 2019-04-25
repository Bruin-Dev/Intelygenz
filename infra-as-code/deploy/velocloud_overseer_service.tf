resource "aws_alb_target_group" "mettel-automation-pro-velocloud-overseer" {
  name = "${var.environment}-velocloud-overseer"
  port = 80
  protocol = "HTTP"
  vpc_id = "${aws_vpc.mettel-automation-pro-vpc.id}"
  target_type = "ip"

  health_check {
    path = "/"
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group" "mettel-automation-pro-velocloud-overseer_service" {
  vpc_id = "${aws_vpc.mettel-automation-pro-vpc.id}"
  name = "${var.environment}-velocloud-overseer"
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
    from_port = 80
    to_port = 80
    protocol = "TCP"
    cidr_blocks = [
      "0.0.0.0/0"
    ]
  }

  tags {
    Name = "${var.environment}-velocloud-overseer"
    Environment = "${var.environment}"
  }
}

resource "aws_ecs_service" "mettel-automation-pro-velocloud-overseer" {
  name = "${var.environment}-velocloud-overseer"
  task_definition = "${aws_ecs_task_definition.mettel-automation-pro-velocloud-overseer.family}:${aws_ecs_task_definition.mettel-automation-pro-velocloud-overseer.revision}"
  desired_count = 1
  launch_type = "FARGATE"
  cluster = "${aws_ecs_cluster.mettel-automation-pro.id}"
  health_check_grace_period_seconds = 1800

  network_configuration {
    security_groups = [
      "${aws_security_group.mettel-automation-pro-velocloud-overseer_service.id}"]
    subnets = [
      "${aws_subnet.mettel-automation-pro-private_subnet-1a.id}",
      "${aws_subnet.mettel-automation-pro-private_subnet-1b.id}"]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = "${aws_alb_target_group.mettel-automation-pro-velocloud-overseer.arn}"
    container_name = "velocloud-overseer"
    container_port = 80
  }
}

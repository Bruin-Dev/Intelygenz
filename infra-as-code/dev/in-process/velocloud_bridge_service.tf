resource "aws_alb_target_group" "mettel-automation-velocloud-bridge" {
  name = "${var.ENVIRONMENT}-velocloud-bridge"
  port = 80
  protocol = "HTTP"
  vpc_id = "${aws_vpc.mettel-automation-vpc.id}"
  target_type = "ip"

  health_check {
    path = "/_health"
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group" "automation-velocloud-bridge_service" {
  vpc_id = "${aws_vpc.automation-vpc.id}"
  name = "${var.ENVIRONMENT}-velocloud-bridge"
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

  tags = {
    Name = "${var.ENVIRONMENT}-velocloud-bridge"
    Environment = "${var.ENVIRONMENT}"
  }
}

resource "aws_ecs_service" "automation-velocloud-bridge" {
  name = "${var.ENVIRONMENT}-velocloud-bridge"
  task_definition = "${aws_ecs_task_definition.automation-velocloud-bridge.family}:${aws_ecs_task_definition.automation-velocloud-bridge.revision}"
  desired_count = 1
  launch_type = "FARGATE"
  cluster = "${aws_ecs_cluster.automation.id}"

  network_configuration {
    security_groups = [
      "${aws_security_group.automation-velocloud-bridge_service.id}"]
    subnets = [
      "${aws_subnet.automation-private_subnet-1a.id}",
      "${aws_subnet.automation-private_subnet-1b.id}"]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = "${aws_alb_target_group.automation-velocloud-bridge.arn}"
    container_name = "velocloud-bridge"
    container_port = 80
  }
}

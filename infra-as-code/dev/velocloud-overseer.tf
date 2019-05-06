data "aws_ecr_repository" "automation-velocloud-overseer" {
  name = "${var.environment}-velocloud-overseer"
}

data "template_file" "automation-velocloud-overseer" {
  template = "${file("${path.module}/task-definitions/velocloud_overseer.json")}"

  vars {
    image = "${data.aws_ecr_repository.automation-velocloud-overseer.repository_url}:${var.BUILD_NUMBER}"
    log_group = "${var.environment}"
    log_prefix = "${var.environment}-${var.BUILD_NUMBER}"

    PYTHONUNBUFFERED = "${var.PYTHONUNBUFFERED}"
    NATS_SERVER1 = "nats://${aws_ecs_service.automation-nats-server.name}:4222"
    NATS_CLUSTER_NAME = "${var.NATS_CLUSTER_NAME}"
    VELOCLOUD_CREDENTIALS = "${var.VELOCLOUD_CREDENTIALS}"
    VELOCLOUD_VERIFY_SSL = "${var.VELOCLOUD_VERIFY_SSL}"
  }
}

resource "aws_ecs_task_definition" "automation-velocloud-overseer" {
  family = "${var.environment}-velocloud-overseer"
  container_definitions = "${data.template_file.automation-velocloud-overseer.rendered}"
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "256"
  memory = "512"
  execution_role_arn = "${aws_iam_role.ecs_execution_role.arn}"
  task_role_arn = "${aws_iam_role.ecs_execution_role.arn}"
}

resource "aws_alb_listener" "automation-velocloud-overseer" {
  load_balancer_arn = "${aws_alb.automation-alb.arn}"
  port = "5000"
  protocol = "HTTP"

  default_action {
    target_group_arn = "${aws_alb_target_group.automation-overseer.arn}"
    type = "forward"
  }
}

resource "aws_alb_target_group" "automation-overseer" {
  name = "${var.environment}-overseer"
  port = 5000
  protocol = "HTTP"
  vpc_id = "${aws_vpc.automation-vpc.id}"
  target_type = "ip"
  stickiness = {
    type = "lb_cookie"
    enabled = false
  }

  depends_on = [
    "aws_alb.automation-alb"]

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group" "automation-velocloud-overseer_service" {
  vpc_id = "${aws_vpc.automation-vpc.id}"
  name = "${var.environment}-velocloud-overseer"
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

  tags {
    Name = "${var.environment}-velocloud-overseer"
    Environment = "${var.environment}"
  }
}

resource "aws_ecs_service" "automation-velocloud-overseer" {
  name = "${var.environment}-velocloud-overseer"
  task_definition = "${aws_ecs_task_definition.automation-velocloud-overseer.family}:${aws_ecs_task_definition.automation-velocloud-overseer.revision}"
  desired_count = 1
  launch_type = "FARGATE"
  cluster = "${aws_ecs_cluster.automation.id}"

  network_configuration {
    security_groups = [
      "${aws_security_group.automation-velocloud-overseer_service.id}"]
    subnets = [
      "${aws_subnet.automation-private_subnet-1a.id}",
      "${aws_subnet.automation-private_subnet-1b.id}"]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = "${aws_alb_target_group.automation-overseer.arn}"
    container_name = "velocloud_overseer"
    container_port = 5000
  }
}

data "aws_ecr_repository" "automation-metrics-grafana" {
  name = "${var.environment}-metrics-dashboard/grafana"
}

data "template_file" "automation-metrics-grafana" {
  template = "${file("${path.module}/task-definitions/grafana.json")}"

  vars = {
    image = "${data.aws_ecr_repository.automation-metrics-grafana.repository_url}:${var.BUILD_NUMBER}"
    log_group = "${var.environment}"
    log_prefix = "${var.environment}-${var.BUILD_NUMBER}"
    GF_SECURITY_ADMIN_PASSWORD = "q1w2e3r4"
  }
}

resource "aws_ecs_task_definition" "automation-metrics-grafana" {
  family = "${var.environment}-metrics-grafana"
  container_definitions = "${data.template_file.automation-metrics-grafana.rendered}"
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "512"
  memory = "1024"
  execution_role_arn = "${aws_iam_role.ecs_execution_role.arn}"
  task_role_arn = "${aws_iam_role.ecs_execution_role.arn}"
}

resource "aws_alb_listener" "automation-grafana" {
  load_balancer_arn = "${aws_alb.automation-alb.arn}"
  port = "3000"
  protocol = "HTTP"

  default_action {
    target_group_arn = "${aws_alb_target_group.automation-metrics-grafana.arn}"
    type = "forward"
  }
}

resource "aws_alb_target_group" "automation-metrics-grafana" {
  name = "${var.environment}-metrics-grafana"
  port = 3000
  protocol = "HTTP"
  vpc_id = "${aws_vpc.automation-vpc.id}"
  target_type = "ip"
  stickiness {
    type = "lb_cookie"
    enabled = false
  }

  depends_on = [
    "aws_alb.automation-alb"]

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group" "automation-grafana_service" {
  vpc_id = "${aws_vpc.automation-vpc.id}"
  name = "${var.environment}-metrics-grafana"
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
    from_port = 3000
    to_port = 3000
    protocol = "TCP"
    cidr_blocks = [
      "0.0.0.0/0"
    ]
  }

  tags = {
    Name = "${var.environment}-metrics-grafana"
    Environment = "${var.environment}"
  }
}

resource "aws_ecs_service" "automation-metrics-grafana" {
  name = "${var.environment}-metrics-grafana"
  task_definition = "${aws_ecs_task_definition.automation-metrics-grafana.family}:${aws_ecs_task_definition.automation-metrics-grafana.revision}"
  desired_count = 1
  launch_type = "FARGATE"
  cluster = "${aws_ecs_cluster.automation.id}"

  network_configuration {
    security_groups = [
      "${aws_security_group.automation-grafana_service.id}"]
    subnets = [
      "${aws_subnet.automation-private_subnet-1a.id}",
      "${aws_subnet.automation-private_subnet-1b.id}"]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = "${aws_alb_target_group.automation-metrics-grafana.arn}"
    container_name = "grafana"
    container_port = 3000
  }
}

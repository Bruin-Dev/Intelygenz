data "aws_ecr_repository" "automation-nats-server" {
  name = "automation-nats-streaming-server"
}

data "template_file" "automation-nats-server" {
  template = "${file("${path.module}/task-definitions/nats_server.json")}"

  vars = {
    image = "${data.aws_ecr_repository.automation-nats-server.repository_url}:${var.BUILD_NUMBER}"
    log_group = "${var.ENVIRONMENT}"
    log_prefix = "${var.ENVIRONMENT}-${var.BUILD_NUMBER}"
  }
}

resource "aws_ecs_task_definition" "automation-nats-server" {
  family = "${var.ENVIRONMENT}-nats-server"
  container_definitions = "${data.template_file.automation-nats-server.rendered}"
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "256"
  memory = "1024"
  execution_role_arn = "${data.aws_iam_role.ecs_execution_role.arn}"
  task_role_arn = "${data.aws_iam_role.ecs_execution_role.arn}"
}

resource "aws_alb_listener" "automation-nats" {
  load_balancer_arn = "${aws_alb.automation-alb.arn}"
  port = "8222"
  protocol = "HTTP"

  default_action {
    target_group_arn = "${aws_alb_target_group.automation-nats-server.arn}"
    type = "forward"
  }
}

resource "aws_alb_target_group" "automation-nats-server" {
  name = "${var.ENVIRONMENT}-nats-server"
  port = 8222
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

resource "aws_security_group" "automation-nats_service" {
  vpc_id = "${aws_vpc.automation-vpc.id}"
  name = "${var.ENVIRONMENT}-nats-server"
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
    from_port = 8222
    to_port = 8222
    protocol = "TCP"
    cidr_blocks = [
      "0.0.0.0/0"
    ]
  }

  ingress {
    from_port = 4222
    to_port = 4222
    protocol = "TCP"
    cidr_blocks = [
      "${var.cdir_base}/16"
    ]
  }

  tags = {
    Name = "${var.ENVIRONMENT}-nats-server"
    Environment = "${var.ENVIRONMENT}"
  }
}

resource "aws_service_discovery_service" "nats-server" {
  name = "nats-server"

  dns_config {
    namespace_id = "${aws_service_discovery_private_dns_namespace.automation-zone.id}"

    dns_records {
      ttl = 10
      type = "A"
    }

    routing_policy = "MULTIVALUE"
  }

  health_check_custom_config {
    failure_threshold = 1
  }
}

resource "aws_ecs_service" "automation-nats-server" {
  name = "${var.ENVIRONMENT}-nats-server"
  task_definition = "${aws_ecs_task_definition.automation-nats-server.family}:${aws_ecs_task_definition.automation-nats-server.revision}"
  desired_count = 1
  launch_type = "FARGATE"
  cluster = "${aws_ecs_cluster.automation.id}"

  network_configuration {
    security_groups = [
      "${aws_security_group.automation-nats_service.id}"]
    subnets = [
      "${aws_subnet.automation-private_subnet-1a.id}",
      "${aws_subnet.automation-private_subnet-1b.id}"]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = "${aws_alb_target_group.automation-nats-server.arn}"
    container_name = "nats-streaming"
    container_port = 8222
  }

  service_registries {
    registry_arn = "${aws_service_discovery_service.nats-server.arn}"
  }
}

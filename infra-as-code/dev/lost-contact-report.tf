data "aws_ecr_repository" "automation-lost-contact-report" {
  name = "automation-lost-contact-report"
}

data "template_file" "automation-lost-contact-report" {
  template = "${file("${path.module}/task-definitions/lost-contact-report.json")}"

  vars = {
    image = "${data.aws_ecr_repository.automation-lost-contact-report.repository_url}:${var.BUILD_NUMBER}"
    log_group = "${var.ENVIRONMENT}"
    log_prefix = "${var.ENVIRONMENT}-${var.BUILD_NUMBER}"

    PYTHONUNBUFFERED = "${var.PYTHONUNBUFFERED}"
    NATS_SERVER1 = "nats://nats-server.${var.ENVIRONMENT}.local:4222"
    NATS_CLUSTER_NAME = "${var.NATS_CLUSTER_NAME}"
    LOST_CONTACT_RECIPIENT = "${var.LOST_CONTACT_RECIPIENT}"
  }
}

resource "aws_ecs_task_definition" "automation-lost-contact-report" {
  family = "${var.ENVIRONMENT}-lost-contact-report"
  container_definitions = "${data.template_file.automation-lost-contact-report.rendered}"
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "256"
  memory = "512"
  execution_role_arn = "${data.aws_iam_role.ecs_execution_role.arn}"
  task_role_arn = "${data.aws_iam_role.ecs_execution_role.arn}"
}

resource "aws_security_group" "automation-lost-contact-report_service" {
  vpc_id = "${aws_vpc.automation-vpc.id}"
  name = "${var.ENVIRONMENT}-lost-contact-report"
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

  ingress {
    from_port = 9090
    to_port = 9090
    protocol = "TCP"
    cidr_blocks = [
      "${var.cdir_base}/16"
    ]
  }

  tags = {
    Name = "${var.ENVIRONMENT}-lost-contact-report"
    Environment = "${var.ENVIRONMENT}"
  }
}

resource "aws_service_discovery_service" "lost-contact-report" {
  name = "lost-contact-report"

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

resource "aws_ecs_service" "automation-lost-contact-report" {
  name = "${var.ENVIRONMENT}-lost-contact-report"
  task_definition = "${aws_ecs_task_definition.automation-lost-contact-report.family}:${aws_ecs_task_definition.automation-lost-contact-report.revision}"
  desired_count = 1
  launch_type = "FARGATE"
  cluster = "${aws_ecs_cluster.automation.id}"

  network_configuration {
    security_groups = [
      "${aws_security_group.automation-lost-contact-report_service.id}"]
    subnets = [
      "${aws_subnet.automation-private_subnet-1a.id}"]
    assign_public_ip = false
  }

  service_registries {
    registry_arn = "${aws_service_discovery_service.lost-contact-report.arn}"
  }
}

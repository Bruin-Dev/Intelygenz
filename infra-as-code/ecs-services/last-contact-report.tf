data "aws_ecr_repository" "automation-last-contact-report" {
  name = "automation-last-contact-report"
}

data "template_file" "automation-last-contact-report" {
  template = "${file("${path.module}/task-definitions/last_contact_report.json")}"

  vars = {
    image = "${data.aws_ecr_repository.automation-last-contact-report.repository_url}:${var.BUILD_NUMBER}"
    log_group = "${var.ENVIRONMENT}"
    log_prefix = "${var.ENVIRONMENT}-${var.BUILD_NUMBER}"

    PYTHONUNBUFFERED = "${var.PYTHONUNBUFFERED}"
    NATS_SERVER1 = "nats://nats-server.${var.ENVIRONMENT}.local:4222"
    NATS_CLUSTER_NAME = "${var.NATS_CLUSTER_NAME}"
    LAST_CONTACT_RECIPIENT = "${var.LAST_CONTACT_RECIPIENT}"
  }
}

resource "aws_ecs_task_definition" "automation-last-contact-report" {
  family = "${var.ENVIRONMENT}-last-contact-report"
  container_definitions = "${data.template_file.automation-last-contact-report.rendered}"
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "256"
  memory = "512"
  execution_role_arn = "${data.terraform_remote_state.tfstate-dev-resources.ecs_execution_role}"
  task_role_arn = "${data.terraform_remote_state.tfstate-dev-resources.ecs_execution_role}"
}

resource "aws_security_group" "automation-last-contact-report_service" {
  vpc_id = "${data.terraform_remote_state.tfstate-dev-resources.vpc_automation_id}"
  name = "${var.ENVIRONMENT}-last-contact-report"
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
    Name = "${var.ENVIRONMENT}-last-contact-report"
    Environment = "${var.ENVIRONMENT}"
  }
}

resource "aws_service_discovery_service" "last-contact-report" {
  name = "last-contact-report"

  dns_config {
    namespace_id = "${data.terraform_remote_state.tfstate-dev-resources.aws_service_discovery_automation-zone_id}"

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

resource "aws_ecs_service" "automation-last-contact-report" {
  name = "${var.ENVIRONMENT}-last-contact-report"
  task_definition = "${aws_ecs_task_definition.automation-last-contact-report.family}:${aws_ecs_task_definition.automation-last-contact-report.revision}"
  desired_count = 1
  launch_type = "FARGATE"
  cluster = "${data.terraform_remote_state.tfstate-dev-resources.automation_cluster_id}"

  network_configuration {
    security_groups = [
      "${aws_security_group.automation-last-contact-report_service.id}"]
    subnets = [
      "${data.terraform_remote_state.tfstate-dev-resources.subnet_automation-private-1a}"]
    assign_public_ip = false
  }

  service_registries {
    registry_arn = "${aws_service_discovery_service.last-contact-report.arn}"
  }
}

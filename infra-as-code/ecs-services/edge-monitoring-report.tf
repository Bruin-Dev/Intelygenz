data "aws_ecr_repository" "automation-edge-monitoring-report" {
  name = "automation-edge-monitoring-report"
}

data "template_file" "automation-edge-monitoring-report" {
  template = "${file("${path.module}/task-definitions/edge_monitoring_report.json")}"

  vars = {
    image = "${data.aws_ecr_repository.automation-edge-monitoring-report.repository_url}:${var.BUILD_NUMBER}"
    log_group = "${var.ENVIRONMENT}"
    log_prefix = "${var.ENVIRONMENT}-${var.BUILD_NUMBER}"

    PYTHONUNBUFFERED = "${var.PYTHONUNBUFFERED}"
    NATS_SERVER1 = "nats://nats-server.${var.ENVIRONMENT}.local:4222"
    NATS_CLUSTER_NAME = "${var.NATS_CLUSTER_NAME}"
    LAST_CONTACT_RECIPIENT = "${var.LAST_CONTACT_RECIPIENT}"
  }
}

resource "aws_ecs_task_definition" "automation-edge-monitoring-report" {
  family = "${var.ENVIRONMENT}-edge-monitoring-report"
  container_definitions = "${data.template_file.automation-edge-monitoring-report.rendered}"
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "256"
  memory = "512"
  execution_role_arn = "${data.terraform_remote_state.tfstate-dev-resources.outputs.ecs_execution_role}"
  task_role_arn = "${data.terraform_remote_state.tfstate-dev-resources.outputs.ecs_execution_role}"
}

resource "aws_security_group" "automation-edge-monitoring-report_service" {
  vpc_id = "${data.terraform_remote_state.tfstate-dev-resources.outputs.vpc_automation_id}"
  name = "${var.ENVIRONMENT}-edge-monitoring-report"
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
    Name = "${var.ENVIRONMENT}-edge-monitoring-report"
    Environment = "${var.ENVIRONMENT}"
  }
}

resource "aws_service_discovery_service" "edge-monitoring-report" {
  name = "edge-monitoring-report"

  dns_config {
    namespace_id = "${data.terraform_remote_state.tfstate-dev-resources.outputs.aws_service_discovery_automation-zone_id}"

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

resource "aws_ecs_service" "automation-edge-monitoring-report" {
  name = "${var.ENVIRONMENT}-edge-monitoring-report"
  task_definition = "${aws_ecs_task_definition.automation-edge-monitoring-report.family}:${aws_ecs_task_definition.automation-edge-monitoring-report.revision}"
  desired_count = 1
  launch_type = "FARGATE"
  cluster = "${data.terraform_remote_state.tfstate-dev-resources.outputs.automation_cluster_id}"

  network_configuration {
    security_groups = [
      "${aws_security_group.automation-edge-monitoring-report_service.id}"]
    subnets = [
      "${data.terraform_remote_state.tfstate-dev-resources.outputs.subnet_automation-private-1a}"]
    assign_public_ip = false
  }

  service_registries {
    registry_arn = "${aws_service_discovery_service.edge-monitoring-report.arn}"
  }
}

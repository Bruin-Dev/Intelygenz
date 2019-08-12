data "aws_ecr_repository" "automation-metrics-prometheus" {
  name = "automation-metrics-dashboard/prometheus"
}

data "template_file" "automation-metrics-prometheus" {
  template = "${file("${path.module}/task-definitions/prometheus.json")}"

  vars = {
    image = "${data.aws_ecr_repository.automation-metrics-prometheus.repository_url}:${var.BUILD_NUMBER}"
    log_group = "${var.ENVIRONMENT}"
    log_prefix = "${var.ENVIRONMENT}-${var.BUILD_NUMBER}"
  }
}

resource "aws_ecs_task_definition" "automation-metrics-prometheus" {
  family = "${var.ENVIRONMENT}-metrics-prometheus"
  container_definitions = "${data.template_file.automation-metrics-prometheus.rendered}"
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "256"
  memory = "512"
  execution_role_arn = "${data.terraform_remote_state.tfstate-dev-resources.outputs.ecs_execution_role}"
  task_role_arn = "${data.terraform_remote_state.tfstate-dev-resources.outputs.ecs_execution_role}"
}

resource "aws_security_group" "automation-metrics-prometheus_service" {
  vpc_id = "${data.terraform_remote_state.tfstate-dev-resources.outputs.vpc_automation_id}"
  name = "${var.ENVIRONMENT}-metrics-prometheus"
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
    from_port = 9090
    to_port = 9090
    protocol = "TCP"
    cidr_blocks = [
      "0.0.0.0/0"
    ]
  }

  tags = {
    Name = "${var.ENVIRONMENT}-metrics-prometheus"
    Environment = "${var.ENVIRONMENT}"
  }
}

resource "aws_service_discovery_service" "metrics-prometheus" {
  name = "prometheus"

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

resource "aws_ecs_service" "automation-metrics-prometheus" {
  name = "${var.ENVIRONMENT}-metrics-prometheus"
  task_definition = "${aws_ecs_task_definition.automation-metrics-prometheus.family}:${aws_ecs_task_definition.automation-metrics-prometheus.revision}"
  desired_count = 1
  launch_type = "FARGATE"
  cluster = "${data.terraform_remote_state.tfstate-dev-resources.outputs.automation_cluster_id}"

  network_configuration {
    security_groups = [
      "${aws_security_group.automation-metrics-prometheus_service.id}"]
    subnets = [
      "${data.terraform_remote_state.tfstate-dev-resources.outputs.subnet_automation-private-1a}"]
    assign_public_ip = false
  }

  service_registries {
    registry_arn = "${aws_service_discovery_service.metrics-prometheus.arn}"
  }
}

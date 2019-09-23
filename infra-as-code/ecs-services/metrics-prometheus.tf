data "aws_ecr_repository" "automation-metrics-prometheus" {
  name = "automation-metrics-dashboard/prometheus"
}

data "template_file" "automation-metrics-prometheus" {
  template = file("${path.module}/task-definitions/prometheus.json")

  vars = {
    image = local.automation-metrics-prometheus-image
    log_group = var.ENVIRONMENT
    log_prefix = local.log_prefix
  }
}

resource "aws_ecs_task_definition" "automation-metrics-prometheus" {
  family = local.automation-metrics-prometheus-ecs_task_definition-family
  container_definitions = data.template_file.automation-metrics-prometheus.rendered
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "256"
  memory = "512"
  execution_role_arn = data.terraform_remote_state.tfstate-dev-resources.outputs.ecs_execution_role
  task_role_arn = data.terraform_remote_state.tfstate-dev-resources.outputs.ecs_execution_role
}

resource "aws_security_group" "automation-metrics-prometheus_service" {
  vpc_id = data.terraform_remote_state.tfstate-dev-resources.outputs.vpc_automation_id
  name = local.automation-metrics-prometheus-service-security_group-name
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
    Name = local.automation-metrics-prometheus-service-security_group-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_service_discovery_service" "metrics-prometheus" {
  name = "prometheus"

  dns_config {
    namespace_id = data.terraform_remote_state.tfstate-dev-resources.outputs.aws_service_discovery_automation-zone_id

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
  name = local.automation-metrics-prometheus-ecs_service-name
  task_definition = local.automation-metrics-prometheus-ecs_service-task_definition
  desired_count = 1
  launch_type = "FARGATE"
  cluster = data.terraform_remote_state.tfstate-dev-resources.outputs.automation_cluster_id

  network_configuration {
    security_groups = [
      aws_security_group.automation-metrics-prometheus_service.id]
    subnets = [
      data.terraform_remote_state.tfstate-dev-resources.outputs.subnet_automation-private-1a,
      data.terraform_remote_state.tfstate-dev-resources.outputs.subnet_automation-private-1b]
    assign_public_ip = false
  }

  service_registries {
    registry_arn = "${aws_service_discovery_service.metrics-prometheus.arn}"
  }
}

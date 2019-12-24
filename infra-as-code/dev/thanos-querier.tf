data "aws_ecr_repository" "automation-metrics-thanos-querier" {
  name = "automation-metrics-dashboard/thanos-querier"
}

data "template_file" "automation-metrics-thanos-querier" {
  template = file("${path.module}/task-definitions/thanos_querier.json")

  vars = {
    image = local.automation-metrics-thanos-querier-image
    log_group = var.ENVIRONMENT
    log_prefix = local.log_prefix
    HTTP_PORT = local.automation-metrics-thanos-querier-HTTP_PORT
    thanos_sidecar_url = local.automation-metrics-thanos-sidecar-url
    thanos_store_gateway_url = local.automation-metrics-thanos-store-gateway-url
  }
}

resource "aws_ecs_task_definition" "automation-metrics-thanos-querier" {
  family = local.automation-metrics-thanos-querier-ecs_task_definition-family
  container_definitions = data.template_file.automation-metrics-thanos-querier.rendered
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "256"
  memory = "512"
  execution_role_arn = data.aws_iam_role.ecs_execution_role.arn
  task_role_arn = data.aws_iam_role.ecs_execution_role.arn
}

resource "aws_security_group" "automation-metrics-thanos-querier_service" {
  vpc_id = data.terraform_remote_state.tfstate-network-resources.outputs.vpc_automation_id
  name = local.automation-metrics-thanos-querier-security_group-name
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
    from_port = local.automation-metrics-thanos-querier-HTTP_PORT
    to_port = local.automation-metrics-thanos-querier-HTTP_PORT
    protocol = "TCP"
    cidr_blocks = [
      "0.0.0.0/0"
    ]
  }

  tags = {
    Name = local.automation-metrics-thanos-querier-security_group-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_service_discovery_service" "metrics-thanos-querier" {
  name = local.automation-metrics-thanos-querier-service_discovery_service-name

  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.automation-zone.id

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

resource "aws_ecs_service" "automation-metrics-thanos-querier" {
  name = local.automation-metrics-thanos-querier-ecs_service-name
  task_definition = local.automation-metrics-thanos-querier-ecs_service-task_definition
  desired_count = var.metrics_thanos_store_gateway_desired_tasks
  launch_type = "FARGATE"
  cluster = aws_ecs_cluster.automation.id

  network_configuration {
    security_groups = [
      aws_security_group.automation-metrics-thanos-querier_service.id]
    subnets = [
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1a.id,
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1b.id]
    assign_public_ip = false
  }

  service_registries {
    registry_arn = aws_service_discovery_service.metrics-thanos-querier.arn
  }

  depends_on = [ null_resource.nats-server-healtcheck ]
}
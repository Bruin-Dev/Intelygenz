data "aws_ecr_repository" "automation-metrics-prometheus" {
  name = "automation-metrics-dashboard/prometheus"
}

data "aws_ecr_repository" "automation-metrics-thanos" {
  name = "automation-metrics-dashboard/thanos"
}

data "template_file" "automation-metrics-prometheus" {
  template = file("${path.module}/task-definitions/prometheus.json")

  vars = {
    prometheus_image = local.automation-metrics-prometheus-image
    thanos_image = local.automation-metrics-thanos-image
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
  execution_role_arn = data.aws_iam_role.ecs_execution_role_with_s3.arn
  task_role_arn = data.aws_iam_role.ecs_execution_role_with_s3.arn
  volume {
    name      = "prometheus_storage"
  }
}

resource "aws_security_group" "automation-metrics-prometheus_service" {
  vpc_id = data.terraform_remote_state.tfstate-network-resources.outputs.vpc_automation_id
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

  ingress {
    from_port = 10091
    to_port = 10091
    protocol = "TCP"
    cidr_blocks = [
      "0.0.0.0/0"
    ]
  }

  ingress {
    from_port = 10902
    to_port = 10902
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
  name = local.automation-metrics-prometheus-service_discovery_service-name

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

resource "aws_ecs_service" "automation-metrics-prometheus" {
  name = local.automation-metrics-prometheus-ecs_service-name
  task_definition = local.automation-metrics-prometheus-ecs_service-task_definition
  desired_count = var.metrics_prometheus_desired_tasks
  launch_type = "FARGATE"
  cluster = aws_ecs_cluster.automation.id

  network_configuration {
    security_groups = [
      aws_security_group.automation-metrics-prometheus_service.id]
    subnets = [
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1a.id,
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1b.id]
    assign_public_ip = false
  }

  service_registries {
    registry_arn = aws_service_discovery_service.metrics-prometheus.arn
  }

  depends_on = [ null_resource.nats-server-healtcheck, aws_s3_bucket.prometheus-storage]
}

resource "aws_s3_bucket" "prometheus-storage" {
  bucket = local.automation-metrics-prometheus-s3-storage-name
  acl    = "private"

  tags = {
    Name        = local.automation-metrics-prometheus-s3-storage-tag-Name
    Environment = var.ENVIRONMENT
  }

  force_destroy = true
}

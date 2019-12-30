data "aws_ecr_repository" "automation-metrics-prometheus" {
  name = "automation-metrics-dashboard/prometheus"
}

data "aws_ecr_repository" "automation-metrics-thanos-sidecar" {
  name = "automation-metrics-dashboard/thanos"
}

data "aws_ecr_repository" "automation-metrics-thanos-querier" {
  name = "automation-metrics-dashboard/thanos-querier"
}

data "aws_ecr_repository" "automation-metrics-grafana" {
  name = "automation-metrics-dashboard/grafana"
}

data "aws_ecr_repository" "automation-metrics-thanos-store-gateway" {
  name = "automation-metrics-dashboard/thanos-store-gateway"
}

data "template_file" "automation-metrics-prometheus" {
  template = file("${path.module}/task-definitions/prometheus.json")

  vars = {
    prometheus_image = local.automation-metrics-prometheus-image
    prometheus_HTTP_PORT = local.automation-metrics-prometheus-HTTP_PORT
    prometheus_storage_volume_name = local.automation-metrics-prometheus-volume-name
    prometheus_storage_container_path = local.automation-metrics-prometheus-volume-container_path
    prometheus_tsdb_path = local.automation-metrics-prometheus-tsdb_path
    prometheus_tsdb_retention_time = local.automation-metrics-prometheus-tsdb_retention_time
    prometheus_tsdb_block_duration = local.automation-metrics-prometheus-tsdb_block_duration
    thanos_sidecar_image = local.automation-metrics-thanos-sidecar-image
    thanos_sidecar_GRPC_PORT = local.automation-metrics-thanos-sidecar-GRPC_PORT
    thanos_sidecar_HTTP_PORT = local.automation-metrics-thanos-sidecar-HTTP_PORT
    thanos_sidecar_objstore_config_file = local.automation-metrics-thanos-sidecar-objstore-config_file
    thanos_store_gateway_image = local.automation-metrics-thanos-store-gateway-image
    thanos_store_gateway_GRPC_PORT = local.automation-metrics-thanos-store-gateway-GRPC_PORT
    thanos_store_gateway_HTTP_PORT = local.automation-metrics-thanos-store-gateway-HTTP_PORT
    thanos_store_gateway_objstore_config_file = local.automation-metrics-thanos-store-gateway-config_file
    thanos_querier_image = local.automation-metrics-thanos-querier-image
    thanos_querier_GRPC_PORT = local.automation-metrics-thanos-querier-GRPC_PORT
    thanos_querier_HTTP_PORT = local.automation-metrics-thanos-querier-HTTP_PORT
    grafana_image = local.automation-metrics-grafana-image
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
  cpu = "4096"
  memory = "8192"
  execution_role_arn = data.aws_iam_role.ecs_execution_role_with_s3.arn
  task_role_arn = data.aws_iam_role.ecs_execution_role_with_s3.arn
  volume {
    name      = local.automation-metrics-prometheus-volume-name
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
    from_port = 3000
    to_port = 3000
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

resource "aws_lb_listener" "automation-grafana" {
  load_balancer_arn = aws_lb.automation-alb.arn
  port = "443"
  protocol = "HTTPS"
  certificate_arn = data.aws_acm_certificate.automation.arn

  default_action {
    target_group_arn = aws_lb_target_group.automation-metrics-grafana.arn
    type = "forward"
  }
}

resource "aws_lb_target_group" "automation-metrics-grafana" {
  name = local.automation-metrics-grafana-target_group-name
  port = 3000
  protocol = "HTTP"
  vpc_id = data.terraform_remote_state.tfstate-network-resources.outputs.vpc_automation_id
  target_type = "ip"
  stickiness {
    type = "lb_cookie"
    enabled = false
  }

  lifecycle {
    create_before_destroy = true
  }

  health_check {
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 3
    interval            = 30
    port                = 3000
    matcher             = 200
    protocol            = "HTTP"
    path                = "/api/health"
  }

  tags = {
    Name = local.automation-metrics-grafana-target_group-tag-Name
    Environment = var.ENVIRONMENT
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

  load_balancer {
    target_group_arn = aws_lb_target_group.automation-metrics-grafana.arn
    container_name = "grafana"
    container_port = 3000
  }

  depends_on = [ null_resource.nats-server-healtcheck, aws_s3_bucket.prometheus-storage]
}

resource "aws_s3_bucket" "prometheus-storage" {
  bucket = local.automation-metrics-prometheus-s3-storage-name

  tags = {
    Name        = local.automation-metrics-prometheus-s3-storage-tag-Name
    Environment = var.ENVIRONMENT
  }

  lifecycle_rule {
    enabled = true

    expiration {
      days = local.automation-metrics-prometheus-s3-expiration-days
    }
  }

  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "prometheus-storage-block" {
  bucket = aws_s3_bucket.prometheus-storage.id

  ignore_public_acls = true
  block_public_acls   = true
  block_public_policy = true
  restrict_public_buckets = true

}

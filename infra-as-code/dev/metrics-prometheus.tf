locals {
  // automation-metrics-grafana local vars
  automation-metrics-grafana-image = "${data.aws_ecr_repository.automation-metrics-grafana.repository_url}:${data.external.grafana-build_number.result["image_tag"]}"
  automation-grafana-papertrail_prefix = "grafana-${element(split("-", data.external.grafana-build_number.result["image_tag"]),2)}"
  automation-metrics-grafana-target_group-name = "${var.ENVIRONMENT}-mts-grafana"
  automation-metrics-grafana-target_group-tag-Name = "${var.ENVIRONMENT}-metrics-grafana"

  // automation-metrics-prometheus local vars
  automation-metrics-prometheus-image = "${data.aws_ecr_repository.automation-metrics-prometheus.repository_url}:${data.external.prometheus-build_number.result["image_tag"]}"
  automation-metrics-prometheus-ecs_task_definition-family = "${var.ENVIRONMENT}-metrics-prometheus"
  automation-metrics-prometheus-service-security_group-name = "${var.ENVIRONMENT}-metrics-prometheus"
  automation-metrics-prometheus-service-security_group-tag-Name = "${var.ENVIRONMENT}-metrics-prometheus"
  automation-metrics-prometheus-ecs_service-name = "${var.ENVIRONMENT}-metrics-prometheus"
  automation-metrics-prometheus-ecs_service-task_definition = "${aws_ecs_task_definition.automation-metrics-prometheus.family}:${aws_ecs_task_definition.automation-metrics-prometheus.revision}"
  automation-metrics-prometheus-service_discovery_service-name = "prometheus-${var.ENVIRONMENT}"
  automation-metrics-prometheus-HTTP_PORT = 9090
  automation-metrics-prometheus-tsdb_path = "/prometheus"
  automation-metrics-prometheus-volume-container_path = "/prometheus"
  automation-metrics-prometheus-tsdb_retention_time = "8h"
  automation-metrics-prometheus-tsdb_block_duration = "1h"
  automation-metrics-prometheus-volume-name = "prometheus_storage-${var.ENVIRONMENT}"
  automation-metrics-prometheus-s3-storage-name = "prometheus-storage-${var.ENVIRONMENT}"
  automation-metrics-prometheus-s3-expiration-days = 14
  automation-metrics-prometheus-s3-storage-tag-Name = "${var.ENVIRONMENT}-metrics-prometheus-storage"

  // automation-metrics-thanos-sidecar local vars
  automation-metrics-thanos-sidecar-image = "${data.aws_ecr_repository.automation-metrics-thanos-sidecar.repository_url}:${data.external.thanos-sidecar-build_number.result["image_tag"]}"
  automation-metrics-thanos-sidecar-GRPC_PORT = 10091
  automation-metrics-thanos-sidecar-HTTP_PORT = 10902
  automation-metrics-thanos-sidecar-objstore-config_file = "/tmp/bucket_config.yaml"

  // automation-metrics-thanos-store-gateway local vars
  automation-metrics-thanos-store-gateway-image = "${data.aws_ecr_repository.automation-metrics-thanos-store-gateway.repository_url}:${data.external.thanos-store-gateway-build_number.result["image_tag"]}"
  automation-metrics-thanos-store-gateway-GRPC_PORT = 10901
  automation-metrics-thanos-store-gateway-HTTP_PORT = 19191
  automation-metrics-thanos-store-gateway-config_file = "/tmp/bucket_config.yaml"

  // automation-metrics-thanos-querier local vars
  automation-metrics-thanos-querier-image = "${data.aws_ecr_repository.automation-metrics-thanos-querier.repository_url}:${data.external.thanos-querier-build_number.result["image_tag"]}"
  automation-metrics-thanos-querier-GRPC_PORT = 10999
  automation-metrics-thanos-querier-HTTP_PORT = 19091
}

data "aws_ecr_repository" "automation-metrics-prometheus" {
  name = "automation-metrics-dashboard/prometheus"
}

data "external" "prometheus-build_number" {
  program = [
    "bash",
    "${path.module}/scripts/obtain_latest_image_for_repository.sh",
    data.aws_ecr_repository.automation-metrics-prometheus.name
  ]
}

data "aws_ecr_repository" "automation-metrics-thanos-sidecar" {
  name = "automation-metrics-dashboard/thanos"
}

data "external" "thanos-sidecar-build_number" {
  program = [
    "bash",
    "${path.module}/scripts/obtain_latest_image_for_repository.sh",
    data.aws_ecr_repository.automation-metrics-thanos-sidecar.name
  ]
}

data "aws_ecr_repository" "automation-metrics-thanos-querier" {
  name = "automation-metrics-dashboard/thanos-querier"
}

data "external" "thanos-querier-build_number" {
  program = [
    "bash",
    "${path.module}/scripts/obtain_latest_image_for_repository.sh",
    data.aws_ecr_repository.automation-metrics-thanos-querier.name
  ]
}

data "aws_ecr_repository" "automation-metrics-thanos-store-gateway" {
  name = "automation-metrics-dashboard/thanos-store-gateway"
}

data "external" "thanos-store-gateway-build_number" {
  program = [
    "bash",
    "${path.module}/scripts/obtain_latest_image_for_repository.sh",
    data.aws_ecr_repository.automation-metrics-thanos-store-gateway.name
  ]
}

data "aws_ecr_repository" "automation-metrics-grafana" {
  name = "automation-metrics-dashboard/grafana"
}

data "external" "grafana-build_number" {
  program = [
    "bash",
    "${path.module}/scripts/obtain_latest_image_for_repository.sh",
    data.aws_ecr_repository.automation-metrics-grafana.name
  ]
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
    thanos_sidecar_component_name = "sidecar"
    thanos_store_gateway_image = local.automation-metrics-thanos-store-gateway-image
    thanos_store_gateway_GRPC_PORT = local.automation-metrics-thanos-store-gateway-GRPC_PORT
    thanos_store_gateway_HTTP_PORT = local.automation-metrics-thanos-store-gateway-HTTP_PORT
    thanos_store_gateway_objstore_config_file = local.automation-metrics-thanos-store-gateway-config_file
    thanos_store_gateway_component_name = "store-gateway"
    thanos_querier_image = local.automation-metrics-thanos-querier-image
    thanos_querier_GRPC_PORT = local.automation-metrics-thanos-querier-GRPC_PORT
    thanos_querier_HTTP_PORT = local.automation-metrics-thanos-querier-HTTP_PORT
    grafana_image = local.automation-metrics-grafana-image
    NATS_SERVER1 = local.nats_server1
    REDIS_HOSTNAME = local.redis-hostname
    log_group = var.ENVIRONMENT
    log_prefix = local.log_prefix
    PAPERTRAIL_ACTIVE = var.CURRENT_ENVIRONMENT == "production" ? true : false
    PAPERTRAIL_PREFIX = local.automation-grafana-papertrail_prefix
    PAPERTRAIL_HOST = var.PAPERTRAIL_HOST
    PAPERTRAIL_PORT = var.PAPERTRAIL_PORT
    ENVIRONMENT_NAME = var.ENVIRONMENT_NAME
    ENVIRONMENT = var.ENVIRONMENT
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
  vpc_id = data.aws_vpc.mettel-automation-vpc.id
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

resource "aws_ecs_service" "automation-metrics-prometheus" {
  name = local.automation-metrics-prometheus-ecs_service-name
  task_definition = local.automation-metrics-prometheus-ecs_service-task_definition
  desired_count = var.metrics_prometheus_desired_tasks
  launch_type = "FARGATE"
  cluster = aws_ecs_cluster.automation.id
  count = var.metrics_prometheus_desired_tasks > 0 ? 1 : 0

  network_configuration {
    security_groups = [
      aws_security_group.automation-metrics-prometheus_service.id]
    subnets = data.aws_subnet_ids.mettel-automation-private-subnets.ids
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.automation-metrics-grafana.arn
    container_name = "grafana"
    container_port = 3000
  }

  depends_on = [
    null_resource.nats-server-healthcheck,
    aws_s3_bucket.prometheus-storage,
    aws_elasticache_cluster.automation-redis]
}

data "template_file" "automation-metrics-prometheus-task-definition-output" {
  template = file("${path.module}/task-definitions/task_definition_output_template.json")

  vars = {
    task_definition_arn = aws_ecs_task_definition.automation-metrics-prometheus.arn
  }
}

resource "null_resource" "generate_metrics_prometheus_task_definition_output_json" {
  count = var.metrics_prometheus_desired_tasks > 0 ? 1 : 0

  provisioner "local-exec" {
    command = format("cat <<\"EOF\" > \"%s\"\n%s\nEOF", var.metrics-prometheus-task-definition-json, data.template_file.automation-metrics-prometheus-task-definition-output.rendered)
  }
  triggers = {
    always_run = timestamp()
  }
  depends_on = [aws_ecs_task_definition.automation-metrics-prometheus]
}

resource "null_resource" "metrics-prometheus-healthcheck" {
  count = var.metrics_prometheus_desired_tasks > 0 ? 1 : 0

  depends_on = [aws_ecs_service.automation-metrics-prometheus,
                aws_ecs_task_definition.automation-metrics-prometheus,
                null_resource.nats-server-healthcheck,
                null_resource.generate_metrics_prometheus_task_definition_output_json,
                aws_elasticache_cluster.automation-redis]

  provisioner "local-exec" {
    command = "python3 ci-utils/ecs/task_healthcheck.py -t metrics-prometheus ${var.metrics-prometheus-task-definition-json}"
  }

  triggers = {
    always_run = timestamp()
  }
}

resource "aws_s3_bucket" "prometheus-storage" {
  count = var.metrics_prometheus_desired_tasks > 0 ? 1 : 0

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
  count = var.metrics_prometheus_desired_tasks > 0 ? 1 : 0

  bucket = aws_s3_bucket.prometheus-storage[0].id

  ignore_public_acls = true
  block_public_acls   = true
  block_public_policy = true
  restrict_public_buckets = true

}

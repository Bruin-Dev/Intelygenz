## links-metrics-collector local variables
locals {
  // automation-links-metrics-collector local vars
  automation-links-metrics-collector-image = "${data.aws_ecr_repository.automation-links-metrics-collector[0].repository_url}:${data.external.links-metrics-collector-build_number[0].result["image_tag"]}"
  automation-links-metrics-collector-papertrail_prefix = "links-metrics-collector-${element(split("-", data.external.links-metrics-collector-build_number[0].result["image_tag"]),2)}"
  automation-links-metrics-collector-ecs_task_definition-family = "${var.ENVIRONMENT}-links-metrics-collector"
  automation-links-metrics-collector_service-security_group-name = "${var.ENVIRONMENT}-links-metrics-collector"
  automation-links-metrics-collector-resource-name = "${var.ENVIRONMENT}-links-metrics-collector"
  automation-links-metrics-collector-service-security_group-tag-Name = "${var.ENVIRONMENT}-links-metrics-collector"
  automation-links-metrics-collector-task_definition = "${aws_ecs_task_definition.automation-links-metrics-collector[0].family}:${aws_ecs_task_definition.automation-links-metrics-collector[0].revision}"
  automation-links-metrics-collector-service_discovery_service-name = "links-metrics-collector-${var.ENVIRONMENT}"
}

data "aws_ecr_repository" "automation-links-metrics-collector" {
  count = var.CURRENT_ENVIRONMENT == "production" ? 1 : 0
  name  = "automation-links-metrics-collector"
}

data "external" "links-metrics-collector-build_number" {
  count   = var.CURRENT_ENVIRONMENT == "production" ? 1 : 0
  program = [
    "bash",
    "${path.module}/scripts/obtain_latest_image_for_repository.sh",
    data.aws_ecr_repository.automation-links-metrics-collector[0].name
  ]
}

data "template_file" "automation-links-metrics-collector" {
  count    = var.CURRENT_ENVIRONMENT == "production" ? 1 : 0
  template = file("${path.module}/task-definitions/links_metrics_collector.json")

  vars = {
    image = local.automation-links-metrics-collector-image
    log_group = var.ENVIRONMENT
    log_prefix = local.log_prefix

    MONGODB_USERNAME = var.TICKET_COLLECTOR_MONGO_USERNAME
    MONGODB_PASSWORD = var.TICKET_COLLECTOR_MONGO_PASSWORD
    MONGODB_HOST = var.TICKET_COLLECTOR_MONGO_HOST
    MONGODB_PORT = var.TICKET_COLLECTOR_MONGO_PORT
    CURRENT_ENVIRONMENT = var.CURRENT_ENVIRONMENT
    ENVIRONMENT_NAME = var.ENVIRONMENT_NAME
    PAPERTRAIL_ACTIVE = var.CURRENT_ENVIRONMENT == "production" ? true : false
    PAPERTRAIL_PREFIX = local.automation-links-metrics-collector-papertrail_prefix
    PAPERTRAIL_HOST = var.PAPERTRAIL_HOST
    PAPERTRAIL_PORT = var.PAPERTRAIL_PORT
  }
}

resource "aws_ecs_task_definition" "automation-links-metrics-collector" {
  count  = var.CURRENT_ENVIRONMENT == "production" ? 1 : 0
  family = local.automation-links-metrics-collector-ecs_task_definition-family
  container_definitions = data.template_file.automation-links-metrics-collector[0].rendered
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "256"
  memory = "512"
  execution_role_arn = data.aws_iam_role.ecs_execution_role.arn
  task_role_arn = data.aws_iam_role.ecs_execution_role.arn
}

resource "aws_security_group" "automation-links-metrics-collector_service" {
  count = var.CURRENT_ENVIRONMENT == "production" ? 1 : 0
  vpc_id = data.aws_vpc.mettel-automation-vpc.id
  name = local.automation-links-metrics-collector_service-security_group-name
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

  tags = {
    Name = local.automation-links-metrics-collector-service-security_group-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_service_discovery_service" "links-metrics-collector" {
  count = var.CURRENT_ENVIRONMENT == "production" ? 1 : 0
  name  = local.automation-links-metrics-collector-service_discovery_service-name

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

resource "aws_ecs_service" "automation-links-metrics-collector" {
  count = var.CURRENT_ENVIRONMENT == "production" ? 1 : 0
  name = local.automation-links-metrics-collector-resource-name
  task_definition = local.automation-links-metrics-collector-task_definition
  desired_count = var.links_metrics_collector_desired_tasks
  launch_type = "FARGATE"
  cluster = aws_ecs_cluster.automation.id

  network_configuration {
    security_groups = [
      aws_security_group.automation-links-metrics-collector_service[0].id]
    subnets = data.aws_subnet_ids.mettel-automation-private-subnets.ids
    assign_public_ip = false
  }

  service_registries {
    registry_arn = aws_service_discovery_service.links-metrics-collector[0].arn
  }

  depends_on = [ null_resource.bruin-bridge-healthcheck,
                 null_resource.cts-bridge-healthcheck,
                 null_resource.digi-bridge-healthcheck,
                 null_resource.email-tagger-kre-bridge-healthcheck,
                 null_resource.hawkeye-bridge-healthcheck,
                 null_resource.lit-bridge-healthcheck,
                 null_resource.metrics-prometheus-healthcheck,
                 null_resource.notifier-healthcheck,
                 null_resource.t7-bridge-healthcheck,
                 null_resource.velocloud-bridge-healthcheck]
}

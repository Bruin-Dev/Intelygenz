data "aws_ecr_repository" "automation-hawkeye-customer-cache" {
  name = "automation-hawkeye-customer-cache"
}

data "external" "hawkeye-customer-cache-build_number" {
  program = [
    "bash",
    "${path.module}/scripts/obtain_latest_image_for_repository.sh",
    data.aws_ecr_repository.automation-hawkeye-customer-cache.name
  ]
}

data "template_file" "automation-hawkeye-customer-cache" {
  count = var.hawkeye_customer_cache_desired_tasks > 0 ? 1 : 0

  template = file("${path.module}/task-definitions/customer_cache.json")

  vars = {
    image = local.automation-hawkeye-customer-cache-image
    log_group = var.ENVIRONMENT
    log_prefix = local.log_prefix

    PYTHONUNBUFFERED = var.PYTHONUNBUFFERED
    NATS_SERVER1 = local.nats_server1
    REDIS_HOSTNAME = local.redis-hostname
    PAPERTRAIL_ACTIVE = var.CURRENT_ENVIRONMENT == "production" ? true : false
    PAPERTRAIL_PREFIX = local.automation-hawkeye-customer-cache-papertrail_prefix
    PAPERTRAIL_HOST = var.PAPERTRAIL_HOST
    PAPERTRAIL_PORT = var.PAPERTRAIL_PORT
    ENVIRONMENT_NAME = var.ENVIRONMENT_NAME
    REDIS_CUSTOMER_CACHE_HOSTNAME = local.automation-redis-customer-cache-hostname
  }
}

resource "aws_ecs_task_definition" "automation-hawkeye-customer-cache" {
  count = var.hawkeye_customer_cache_desired_tasks > 0 ? 1 : 0

  family = local.automation-hawkeye-customer-cache-ecs_task_definition-family
  container_definitions = data.template_file.automation-hawkeye-customer-cache[0].rendered
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "256"
  memory = "512"
  execution_role_arn = data.aws_iam_role.ecs_execution_role.arn
  task_role_arn = data.aws_iam_role.ecs_execution_role.arn
}

resource "aws_security_group" "automation-hawkeye-customer-cache_service" {
  count = var.hawkeye_customer_cache_desired_tasks > 0 ? 1 : 0

  vpc_id = data.terraform_remote_state.tfstate-network-resources.outputs.vpc_automation_id
  name = local.automation-hawkeye-customer-cache_service-security_group-name
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
    Name = local.automation-hawkeye-customer-cache-service-security_group-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_service_discovery_service" "hawkeye-customer-cache" {
  count = var.hawkeye_customer_cache_desired_tasks > 0 ? 1 : 0

  name = local.automation-hawkeye-customer-cache-service_discovery_service-name

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

resource "aws_ecs_service" "automation-hawkeye-customer-cache" {
  count = var.hawkeye_customer_cache_desired_tasks > 0 ? 1 : 0

  name = local.automation-hawkeye-customer-cache-resource-name
  task_definition = local.automation-hawkeye-customer-cache-task_definition
  desired_count = var.hawkeye_customer_cache_desired_tasks
  launch_type = "FARGATE"
  cluster = aws_ecs_cluster.automation.id

  network_configuration {
    security_groups = [
      aws_security_group.automation-hawkeye-customer-cache_service[0].id]
    subnets = [
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1a.id,
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1b.id]
    assign_public_ip = false
  }

  service_registries {
    registry_arn = aws_service_discovery_service.hawkeye-customer-cache[0].arn
  }

  depends_on = [ null_resource.bruin-bridge-healthcheck,
                 null_resource.velocloud-bridge-healthcheck,
                 null_resource.hawkeye-bridge-healthcheck,
                 null_resource.t7-bridge-healthcheck,
                 null_resource.notifier-healthcheck,
                 null_resource.metrics-prometheus-healthcheck ]
}

data "aws_ecr_repository" "automation-service-outage-monitor" {
  name = "automation-service-outage-monitor"
}

data "external" "service-outage-monitor-build_number" {
  program = [
    "bash",
    "${path.module}/scripts/obtain_latest_image_for_repository.sh",
    data.aws_ecr_repository.automation-service-outage-monitor.name
  ]
}

data "template_file" "automation-service-outage-monitor-triage" {
  template = file("${path.module}/task-definitions/service_outage_monitor.json")

  vars = {
    container_name = local.automation-service-outage-monitor-triage-container_name
    image = local.automation-service-outage-monitor-image
    log_group = var.ENVIRONMENT
    log_prefix = local.log_prefix

    PYTHONUNBUFFERED = var.PYTHONUNBUFFERED
    NATS_SERVER1 = local.nats_server1
    CURRENT_ENVIRONMENT = var.CURRENT_ENVIRONMENT
    LAST_CONTACT_RECIPIENT = var.LAST_CONTACT_RECIPIENT
    REDIS_HOSTNAME = local.redis-hostname
    PAPERTRAIL_ACTIVE = var.CURRENT_ENVIRONMENT == "production" ? true : false
    PAPERTRAIL_PREFIX = local.automation-service-outage-monitor-triage-papertrail_prefix
    PAPERTRAIL_HOST = var.PAPERTRAIL_HOST
    PAPERTRAIL_PORT = var.PAPERTRAIL_PORT
    ENVIRONMENT_NAME = var.ENVIRONMENT_NAME
    VELOCLOUD_HOSTS = local.automation-service-outage-monitor-velocloud_hosts_triage
    VELOCLOUD_HOSTS_FILTER = local.automation-service-outage-monitor-velocloud_hosts_filter
    ENABLE_TRIAGE_MONITORING = local.automation-service-outage-monitor-velocloud_hosts_triage == "" ? 1 : 0
  }
}

resource "aws_ecs_task_definition" "automation-service-outage-monitor-triage" {
  family = local.automation-service-outage-monitor-triage-ecs_task_definition-family
  container_definitions = data.template_file.automation-service-outage-monitor-triage.rendered
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "2048"
  memory = "4096"
  execution_role_arn = data.aws_iam_role.ecs_execution_role.arn
  task_role_arn = data.aws_iam_role.ecs_execution_role.arn
}

resource "aws_security_group" "automation-service-outage-monitor-triage_service" {
  vpc_id = data.terraform_remote_state.tfstate-network-resources.outputs.vpc_automation_id
  name = local.automation-service-outage-monitor-triage-service-security_group-name
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
      var.cidr_base[var.CURRENT_ENVIRONMENT]
    ]
  }

  tags = {
    Name = local.automation-service-outage-monitor-triage-service-security_group-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_service_discovery_service" "service-outage-monitor-triage" {
  name = local.automation-service-outage-monitor-triage-service_discovery_service-name

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

resource "aws_ecs_service" "automation-service-outage-monitor-triage" {
  name = local.automation-service-outage-monitor-triage-ecs_service-name
  task_definition = local.automation-service-outage-monitor-triage-ecs_service-task_definition
  desired_count = var.service_outage_monitor_triage_desired_tasks
  launch_type = "FARGATE"
  cluster = aws_ecs_cluster.automation.id
  count = var.service_outage_monitor_triage_desired_tasks > 0 ? 1 : 0

  network_configuration {
    security_groups = [
      aws_security_group.automation-service-outage-monitor-triage_service.id]
    subnets = [
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1a.id,
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1b.id]
    assign_public_ip = false
  }

  service_registries {
    registry_arn = aws_service_discovery_service.service-outage-monitor-triage.arn
  }

  depends_on = [ null_resource.bruin-bridge-healthcheck,
                 null_resource.cts-bridge-healthcheck,
                 null_resource.lit-bridge-healthcheck,
                 null_resource.metrics-prometheus-healthcheck,
                 null_resource.notifier-healthcheck,
                 null_resource.velocloud-bridge-healthcheck,
                 null_resource.t7-bridge-healthcheck]
}

data "aws_ecr_repository" "automation-sites-monitor" {
  name = "automation-sites-monitor"
}

data "template_file" "automation-sites-monitor" {
  template = file("${path.module}/task-definitions/sites_monitor.json")

  vars = {
    image = local.automation-sites-monitor-image
    log_group = var.ENVIRONMENT
    log_prefix = local.automation-sites-monitor-log_prefix

    PYTHONUNBUFFERED = var.PYTHONUNBUFFERED
    NATS_SERVER1 = local.nats_server1
    MONITORING_SECONDS = var.MONITORING_SECONDS
    LAST_CONTACT_RECIPIENT = var.LAST_CONTACT_RECIPIENT
    REDIS_HOSTNAME = local.redis-hostname
  }
}

resource "aws_ecs_task_definition" "automation-sites-monitor" {
  family = local.automation-sites-monitor-ecs_task_definition-family
  container_definitions = data.template_file.automation-sites-monitor.rendered
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "256"
  memory = "512"
  execution_role_arn = data.aws_iam_role.ecs_execution_role.arn
  task_role_arn = data.aws_iam_role.ecs_execution_role.arn
}

resource "aws_security_group" "automation-sites-monitor_service" {
  vpc_id = data.terraform_remote_state.tfstate-network-resources.outputs.vpc_automation_id
  name = local.automation-sites-monitor-service-security_group-name
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
    Name = local.automation-sites-monitor-service-security_group-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_service_discovery_service" "sites-monitor" {
  name = local.automation-sites-monitor-service_discovery_service-name

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

resource "aws_ecs_service" "automation-sites-monitor" {
  name = local.automation-sites-monitor-ecs_service-name
  task_definition = local.automation-sites-monitor-ecs_service-task_definition
  desired_count = var.sites_monitor_desired_tasks
  launch_type = "FARGATE"
  cluster = aws_ecs_cluster.automation.id
  count = var.sites_monitor_desired_tasks != 0 ? 1 : 0

  network_configuration {
    security_groups = [
      aws_security_group.automation-sites-monitor_service.id]
    subnets = [
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1a.id,
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1b.id]
    assign_public_ip = false
  }

  service_registries {
    registry_arn = aws_service_discovery_service.sites-monitor.arn
  }

  depends_on = [ null_resource.bruin-bridge-healthcheck,
                 null_resource.cts-bridge-healthcheck,
                 null_resource.lit-bridge-healthcheck,
                 null_resource.velocloud-bridge-healthcheck,
                 null_resource.t7-bridge-healthcheck,
                 null_resource.notifier-healthcheck,
                 null_resource.metrics-prometheus-healthcheck ]
}

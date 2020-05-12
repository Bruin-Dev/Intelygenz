data "template_file" "automation-service-outage-monitor-1" {
  count = var.service_outage_monitor_1_desired_tasks > 0 ? 1 : 0
  template = file("${path.module}/task-definitions/service_outage_monitor.json")

  vars = {
    container_name = local.automation-service-outage-monitor-1-container_name
    image = local.automation-service-outage-monitor-image
    log_group = var.ENVIRONMENT
    log_prefix = local.log_prefix

    PYTHONUNBUFFERED = var.PYTHONUNBUFFERED
    NATS_SERVER1 = local.nats_server1
    CURRENT_ENVIRONMENT = var.CURRENT_ENVIRONMENT
    LAST_CONTACT_RECIPIENT = var.LAST_CONTACT_RECIPIENT
    REDIS_HOSTNAME = local.redis-hostname
    VELOCLOUD_HOSTS = var.SERVICE_OUTAGE_MONITOR_1_HOSTS
    ENABLE_TRIAGE_MONITORING = var.SERVICE_OUTAGE_MONITOR_1_HOSTS == "" ? 1 : 0
    VELOCLOUD_HOSTS_FILTER = var.SERVICE_OUTAGE_MONITOR_1_HOSTS_FILTER
  }
}

resource "aws_ecs_task_definition" "automation-service-outage-monitor-1" {
  count = var.service_outage_monitor_1_desired_tasks > 0 ? 1 : 0
  family = local.automation-service-outage-monitor-1-ecs_task_definition-family
  container_definitions = data.template_file.automation-service-outage-monitor-1[0].rendered
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "2048"
  memory = "4096"
  execution_role_arn = data.aws_iam_role.ecs_execution_role.arn
  task_role_arn = data.aws_iam_role.ecs_execution_role.arn
}

resource "aws_security_group" "automation-service-outage-monitor-1_service" {
  count = var.service_outage_monitor_1_desired_tasks > 0 ? 1 : 0
  vpc_id = data.terraform_remote_state.tfstate-network-resources.outputs.vpc_automation_id
  name = local.automation-service-outage-monitor-1-service-security_group-name
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
    Name = local.automation-service-outage-monitor-1-service-security_group-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_service_discovery_service" "service-outage-monitor-1" {
  count = var.service_outage_monitor_1_desired_tasks > 0 ? 1 : 0
  name = local.automation-service-outage-monitor-1-service_discovery_service-name

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

resource "aws_ecs_service" "automation-service-outage-monitor-1" {
  name = local.automation-service-outage-monitor-1-ecs_service-name
  task_definition = local.automation-service-outage-monitor-1-ecs_service-task_definition
  desired_count = var.service_outage_monitor_1_desired_tasks
  launch_type = "FARGATE"
  cluster = aws_ecs_cluster.automation.id
  count = var.service_outage_monitor_1_desired_tasks > 0 ? 1 : 0

  network_configuration {
    security_groups = [
      aws_security_group.automation-service-outage-monitor-1_service[0].id]
    subnets = [
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1a.id,
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1b.id]
    assign_public_ip = false
  }

  service_registries {
    registry_arn = aws_service_discovery_service.service-outage-monitor-1[0].arn
  }

  depends_on = [ null_resource.bruin-bridge-healthcheck,
                 null_resource.velocloud-bridge-healthcheck,
                 null_resource.t7-bridge-healthcheck,
                 null_resource.notifier-healthcheck,
                 null_resource.metrics-prometheus-healthcheck ]
}

data "aws_ecr_repository" "automation-lumin-billing-report" {
  name = "automation-lumin-billing-report"
}

data "external" "lumin-billing-report-build_number" {
  program = [
    "bash",
    "${path.module}/scripts/obtain_latest_image_for_repository.sh",
    data.aws_ecr_repository.automation-lumin-billing-report.name
  ]
}

data "template_file" "automation-lumin-billing-report" {
  template = file("${path.module}/task-definitions/lumin_billing_report.json")

  vars = {
    image = local.automation-lumin-billing-report-image
    log_group = var.ENVIRONMENT
    log_prefix = local.log_prefix

    PYTHONUNBUFFERED = var.PYTHONUNBUFFERED
    LUMIN_URI = var.LUMIN_URI
    LUMIN_TOKEN = var.LUMIN_TOKEN
    CUSTOMER_NAME = var.CUSTOMER_NAME_BILLING_REPORT
    BILLING_RECIPIENT = var.BILLING_RECIPIENT_REPORT
    EMAIL_ACC_PWD = var.EMAIL_ACC_PWD
    PAPERTRAIL_ACTIVE = var.CURRENT_ENVIRONMENT == "production" ? true : false
    PAPERTRAIL_PREFIX = local.automation-lumin-billing-report-papertrail_prefix
    PAPERTRAIL_HOST = var.PAPERTRAIL_HOST
    PAPERTRAIL_PORT = var.PAPERTRAIL_PORT
    ENVIRONMENT_NAME = var.ENVIRONMENT_NAME
  }
}

resource "aws_ecs_task_definition" "automation-lumin-billing-report" {
  family = local.automation-lumin-billing-report-ecs_task_definition-family
  container_definitions = data.template_file.automation-lumin-billing-report.rendered
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "256"
  memory = "512"
  execution_role_arn = data.aws_iam_role.ecs_execution_role.arn
  task_role_arn = data.aws_iam_role.ecs_execution_role.arn
}

resource "aws_security_group" "automation-lumin-billing-report_service" {
  vpc_id = data.terraform_remote_state.tfstate-network-resources.outputs.vpc_automation_id
  name = local.automation-lumin-billing-report-service-security_group-name
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
      var.cidr_base[var.CURRENT_ENVIRONMENT]
    ]
  }

  tags = {
    Name = local.automation-lumin-billing-report-service-security_group-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_service_discovery_service" "lumin-billing-report" {
  name = local.automation-lumin-billing-report-service_discovery_service-name

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

resource "aws_ecs_service" "automation-lumin-billing-report" {
  name = local.automation-lumin-billing-report-resource-name
  task_definition = local.automation-lumin-billing-report-task_definition
  desired_count = var.lumin_billing_report_desired_tasks
  launch_type = "FARGATE"
  cluster = aws_ecs_cluster.automation.id
  count = var.lumin_billing_report_desired_tasks != 0 ? 1 : 0

  network_configuration {
    security_groups = [
      aws_security_group.automation-lumin-billing-report_service.id]
    subnets = [
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1a.id,
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1b.id]
    assign_public_ip = false
  }

  service_registries {
    registry_arn = aws_service_discovery_service.lumin-billing-report.arn
  }

}

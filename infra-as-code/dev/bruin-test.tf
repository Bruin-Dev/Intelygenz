data "aws_ecr_repository" "automation-bruin-test" {
  name = "automation-bruin-test"
}

data "template_file" "automation-bruin-test" {
  template = file("${path.module}/task-definitions/bruin_test.json")

  vars = {
    image = local.automation-bruin-test-image
    log_group = var.ENVIRONMENT
    log_prefix = local.log_prefix

    PYTHONUNBUFFERED = var.PYTHONUNBUFFERED
    BRUIN_CLIENT_ID = var.BRUIN_CLIENT_ID_TEST
    BRUIN_CLIENT_SECRET = var.BRUIN_CLIENT_SECRET_TEST
    BRUIN_LOGIN_URL = var.BRUIN_LOGIN_URL_TEST
    BRUIN_BASE_URL = var.BRUIN_BASE_URL_TEST
  }
}

resource "aws_ecs_task_definition" "automation-bruin-test" {
  family = local.automation-bruin-test-ecs_task_definition-family
  container_definitions = data.template_file.automation-bruin-test.rendered
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "1024"
  memory = "2048"
  execution_role_arn = data.aws_iam_role.ecs_execution_role.arn
  task_role_arn = data.aws_iam_role.ecs_execution_role.arn
}

resource "aws_security_group" "automation-bruin-test_service" {
  vpc_id = data.terraform_remote_state.tfstate-network-resources.outputs.vpc_automation_id
  name = local.automation-bruin-test_service-security_group-name
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
    Name = local.automation-bruin-test-service-security_group-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_service_discovery_service" "bruin-test" {
  name = local.automation-bruin-test-service_discovery_service-name

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

resource "aws_ecs_service" "automation-bruin-test" {
  name = local.automation-bruin-test-resource-name
  task_definition = local.automation-bruin-test-task_definition
  desired_count = var.bruin_test_desired_tasks
  launch_type = "FARGATE"
  cluster = aws_ecs_cluster.automation.id
  count = var.bruin_test_desired_tasks > 0 ? 1 : 0

  network_configuration {
    security_groups = [
      aws_security_group.automation-bruin-test_service.id]
    subnets = [
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1a.id,
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1b.id]
    assign_public_ip = false
  }

  service_registries {
    registry_arn = aws_service_discovery_service.bruin-bridge.arn
  }

  depends_on = [
    aws_elasticache_cluster.automation-redis
  ]
}
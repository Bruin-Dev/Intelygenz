locals {
  // automation-dispatch-portal-frontend local vars
  automation-dispatch-portal-frontend-image = "${data.aws_ecr_repository.automation-dispatch-portal-frontend-nextjs.repository_url}:${data.external.dispatch-portal-frontend-nextjs-build_number.result["image_tag"]}"
  automation-dispatch-portal-frontend-nginx-image = "${data.aws_ecr_repository.automation-dispatch-portal-frontend-nginx.repository_url}:${data.external.dispatch-portal-frontend-nginx-build_number.result["image_tag"]}"
  automation-dispatch-portal-service-security_group-name = "${var.ENVIRONMENT}-dispatch-portal-frontend"
  automation-dispatch-portal-frontend-log_prefix = "${var.ENVIRONMENT}-${var.BUILD_NUMBER}"
  automation-dispatch-portal-frontend-ecs_task_definition-family = "${var.ENVIRONMENT}-dispatch-portal-frontend"
  automation-dispatch-portal-frontend-ecs_task_definition = "${var.ENVIRONMENT}-dispatch-portal-frontend"
  automation-dispatch-portal-frontend-service-security_group-name = "${var.ENVIRONMENT}-dispatch-portal-frontend"
  automation-dispatch-portal-frontend-service-security_group-tag-Name = "${var.ENVIRONMENT}-dispatch-portal-frontend"
  automation-dispatch-portal-frontend-ecs_service-name = "${var.ENVIRONMENT}-dispatch-portal-frontend"
  automation-dispatch-portal-frontend-ecs_service-task_definition = "${aws_ecs_task_definition.automation-dispatch-portal-frontend.family}:${aws_ecs_task_definition.automation-dispatch-portal-frontend.revision}"
  automation-dispatch-portal-target_group-name = "${var.ENVIRONMENT}-disp-prtl"
  automation-dispatch-portal-target_group-tag-Name = "${var.ENVIRONMENT}-dispatch-portal"
  automation-dispatch-portal-frontend-nginx-run-mode = "aws"
}

data "aws_ecr_repository" "automation-dispatch-portal-frontend-nextjs" {
  name = "automation-dispatch-portal-frontend"
}

data "external" "dispatch-portal-frontend-nextjs-build_number" {
  program = [
    "bash",
    "${path.module}/scripts/obtain_latest_image_for_repository.sh",
    data.aws_ecr_repository.automation-dispatch-portal-frontend-nextjs.name
  ]
}

data "aws_ecr_repository" "automation-dispatch-portal-frontend-nginx" {
  name = "automation-dispatch-portal-frontend/nginx"
}

data "external" "dispatch-portal-frontend-nginx-build_number" {
  program = [
    "bash",
    "${path.module}/scripts/obtain_latest_image_for_repository.sh",
    data.aws_ecr_repository.automation-dispatch-portal-frontend-nginx.name
  ]
}

data "template_file" "automation-dispatch-portal-frontend" {
  template = file("${path.module}/task-definitions/dispatch_portal_frontend.json")

  vars = {
    dispatch_portal_frontend_image = local.automation-dispatch-portal-frontend-image
    dispatch_portal_frontend_nginx_image = local.automation-dispatch-portal-frontend-nginx-image
    log_group = var.ENVIRONMENT
    log_prefix = local.log_prefix
    ENVIRONMENT = var.ENVIRONMENT
    CURRENT_ENVIRONMENT = var.CURRENT_ENVIRONMENT
    ENVIRONMENT_NAME = var.ENVIRONMENT_NAME
    PAPERTRAIL_HOST = var.PAPERTRAIL_HOST
    PAPERTRAIL_PORT = var.PAPERTRAIL_PORT
    BUILD_NUMBER = var.BUILD_NUMBER
    RUN_MODE = local.automation-dispatch-portal-frontend-nginx-run-mode
  }
}

resource "aws_ecs_task_definition" "automation-dispatch-portal-frontend" {
  family = local.automation-dispatch-portal-frontend-ecs_task_definition-family
  container_definitions = data.template_file.automation-dispatch-portal-frontend.rendered
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "256"
  memory = "512"
  execution_role_arn = data.aws_iam_role.ecs_execution_role.arn
  task_role_arn = data.aws_iam_role.ecs_execution_role.arn
}

resource "aws_security_group" "automation-dispatch-portal-frontend_service" {
  vpc_id = data.aws_vpc.mettel-automation-vpc.id
  name = local.automation-dispatch-portal-service-security_group-name
  description = "Allow egress from container"

  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = [
      "0.0.0.0/0"]
  }

  ingress {
    from_port = 8080
    to_port = 8080
    protocol = "TCP"
    security_groups = [aws_security_group.automation-dev-inbound.id]
  }

  tags = {
    Name = local.automation-dispatch-portal-frontend-service-security_group-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_ecs_service" "automation-dispatch-portal-frontend" {
  name = local.automation-dispatch-portal-frontend-ecs_service-name
  task_definition = local.automation-dispatch-portal-frontend-ecs_task_definition
  desired_count = var.dispatch_portal_frontend_desired_tasks
  launch_type = "FARGATE"
  cluster = aws_ecs_cluster.automation.id
  count = var.dispatch_portal_frontend_desired_tasks > 0 ? 1 : 0

  network_configuration {
    security_groups = [
      aws_security_group.automation-dispatch-portal-frontend_service.id]
    subnets = data.aws_subnet_ids.mettel-automation-private-subnets.ids
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.automation-dispatch-portal.arn
    container_name = "dispatch-portal-frontend-nginx"
    container_port = 8080
  }

  depends_on = [ null_resource.bruin-bridge-healthcheck,
                 null_resource.cts-bridge-healthcheck,
                 null_resource.digi-bridge-healthcheck,
                 null_resource.email-tagger-kre-bridge-healthcheck,
                 null_resource.lit-bridge-healthcheck,
                 null_resource.velocloud-bridge-healthcheck,
                 null_resource.hawkeye-bridge-healthcheck,
                 null_resource.t7-bridge-healthcheck,
                 null_resource.notifier-healthcheck,
                 null_resource.metrics-prometheus-healthcheck,
                 null_resource.dispatch-portal-backend-healthcheck,
                 aws_lb.automation-alb]
}
data "aws_ecr_repository" "automation-dispatch-portal-frontend-nextjs" {
  name = "automation-dispatch-portal-frontend"
}

data "aws_ecr_repository" "automation-dispatch-portal-frontend-nginx" {
  name = "automation-dispatch-portal-frontend/nginx"
}

data "template_file" "automation-dispatch-portal-frontend" {
  template = file("${path.module}/task-definitions/dispatch_portal_frontend.json")

  vars = {
    dispatch_portal_frontend_image = local.automation-dispatch-portal-frontend-image
    dispatch_portal_frontend_nginx_image = local.automation-dispatch-portal-frontend-nginx-image
    log_group = var.ENVIRONMENT
    log_prefix = local.log_prefix
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
  vpc_id = data.terraform_remote_state.tfstate-network-resources.outputs.vpc_automation_id
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

resource "aws_lb_target_group" "automation-dispatch-portal" {
  name = local.automation-dispatch-portal-target_group-name
  port = 8080
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
    port                = 8080
    matcher             = 200
    protocol            = "HTTP"
    path                = "/health-check"
  }

  tags = {
    Name = local.automation-dispatch-portal-target_group-tag-Name
    Environment = var.ENVIRONMENT
  }

}

resource "aws_alb_listener_rule" "automation-dispatch-portal-path" {
  depends_on   = [ aws_lb_target_group.automation-dispatch-portal ]
  listener_arn = aws_lb_listener.automation-grafana.arn
  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.automation-dispatch-portal.arn
  }
  condition {
    path_pattern {
      values = [
        "/dispatch_portal/*",
        "/dispatch_portal"]
    }
  }
}

resource "aws_ecs_service" "automation-dispatch-portal-frontend" {
  name = local.automation-dispatch-portal-frontend-ecs_service-name
  task_definition = local.automation-dispatch-portal-frontend-ecs_task_definition
  desired_count = var.dispatch_portal_backend_desired_tasks
  launch_type = "FARGATE"
  cluster = aws_ecs_cluster.automation.id
  count = var.dispatch_portal_backend_desired_tasks > 0 ? 1 : 0

  network_configuration {
    security_groups = [
      aws_security_group.automation-dispatch-portal-frontend_service.id]
    subnets = [
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1a.id,
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1b.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.automation-dispatch-portal.arn
    container_name = "dispatch-portal-frontend-nginx"
    container_port = 8080
  }

  depends_on = [ null_resource.bruin-bridge-healthcheck,
                 null_resource.cts-bridge-healthcheck,
                 null_resource.lit-bridge-healthcheck,
                 null_resource.velocloud-bridge-healthcheck,
                 null_resource.t7-bridge-healthcheck,
                 null_resource.notifier-healthcheck,
                 null_resource.metrics-prometheus-healthcheck,
                 aws_lb.automation-alb]
}
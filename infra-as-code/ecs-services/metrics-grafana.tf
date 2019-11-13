data "aws_ecr_repository" "automation-metrics-grafana" {
  name = "automation-metrics-dashboard/grafana"
}

data "template_file" "automation-metrics-grafana" {
  template = file("${path.module}/task-definitions/grafana.json")

  vars = {
    image = local.automation-metrics-grafana-image
    log_group = var.ENVIRONMENT
    log_prefix = local.log_prefix
    GF_SECURITY_ADMIN_PASSWORD = "q1w2e3r4"
  }
}

resource "aws_ecs_task_definition" "automation-metrics-grafana" {
  family = local.automation-metrics-grafana-ecs_task_definition-family
  container_definitions = data.template_file.automation-metrics-grafana.rendered
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "512"
  memory = "1024"
  execution_role_arn = data.terraform_remote_state.tfstate-dev-resources.outputs.ecs_execution_role
  task_role_arn = data.terraform_remote_state.tfstate-dev-resources.outputs.ecs_execution_role
}

resource "aws_lb_listener" "automation-grafana" {
  load_balancer_arn = data.terraform_remote_state.tfstate-dev-resources.outputs.automation_alb_arn
  port = "443"
  protocol = "HTTPS"
  certificate_arn = data.terraform_remote_state.tfstate-dev-resources.outputs.cert_mettel

  default_action {
    target_group_arn = aws_lb_target_group.automation-metrics-grafana.arn
    type = "forward"
  }
}

resource "aws_lb_target_group" "automation-metrics-grafana" {
  name = local.automation-metrics-grafana-target_group-name
  port = 3000
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
    port                = 3000
    matcher             = 200
    protocol            = "HTTP"
    path                = "/api/health"
  }

  tags = {
    Name = local.automation-metrics-grafana-target_group-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_security_group" "automation-grafana_service" {
  vpc_id = data.terraform_remote_state.tfstate-network-resources.outputs.vpc_automation_id
  name = local.automation-metrics-grafana-service-security_group-name
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
    from_port = 3000
    to_port = 3000
    protocol = "TCP"
    cidr_blocks = [
      "0.0.0.0/0"
    ]
  }

  tags = {
    Name = local.automation-metrics-grafana-service-security_group-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_ecs_service" "automation-metrics-grafana" {
  name = local.automation-metrics-grafana-ecs_service-name
  task_definition = local.automation-metrics-grafana-ecs_task_definition
  desired_count = 1
  launch_type = "FARGATE"
  cluster = data.terraform_remote_state.tfstate-dev-resources.outputs.automation_cluster_id

  network_configuration {
    security_groups = [
      aws_security_group.automation-grafana_service.id]
    subnets = [
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1a.id,
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1b.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.automation-metrics-grafana.arn
    container_name = "grafana"
    container_port = 3000
  }
}

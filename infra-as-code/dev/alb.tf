resource "aws_security_group" "automation-dev-inbound" {
  name = local.automation-dev-inbound-security_group-name
  description = "Allowed connections into ALB"
  vpc_id = data.aws_vpc.mettel-automation-vpc.id

  lifecycle {
    create_before_destroy = true
  }

  ingress {
    from_port = 8222
    to_port = 8222
    protocol = "tcp"
    cidr_blocks = [
      "24.5.222.73/32", // US OFFICE
      "76.102.161.105/32", // KEKO HOME
      "76.103.237.82/32", // SANCHO HOME
      "73.158.200.161/32", // BRANDON HOME
      "83.61.20.90/32", // IGZ CALLAO OFFICE 1
      "83.61.8.95/32",  // IGZ CALLAO OFFICE 2
      "83.56.7.26/32",   // IGZ CALLAO OFFICE 3
      "52.51.50.68/32", // IGZ VPN
    ]
  }

  ingress {
    from_port = 443
    to_port = 443
    protocol = "tcp"
    cidr_blocks = [
      "24.5.222.73/32", // US OFFICE
      "76.102.161.105/32", // KEKO HOME
      "76.103.237.82/32", // SANCHO HOME
      "73.158.200.161/32", // BRANDON HOME
      "83.61.20.90/32", // IGZ CALLAO OFFICE 1
      "83.61.8.95/32",  // IGZ CALLAO OFFICE 2
      "83.56.7.26/32",  // IGZ CALLAO OFFICE 3
      "52.51.50.68/32", // IGZ VPN
      "79.146.229.176/32",   // JESUS HOME
      "139.47.71.34/32",    // JC HOME
      "54.73.0.183/32", // IGZ GITLAB RUNNERS
      "216.194.50.82/32", // Brian Sullivan's IP
      "216.194.28.12/32", // Joseph Degeorge's IP
      "216.194.50.83/32",  // MetTel Office IP
      "216.194.28.132/32", // MetTel Office IP
      "216.194.28.130/32",  // MetTel Cisco VPN
      "216.194.28.16/32" // MetTel Fortinet VPN     
    ]
  }

    ingress {
    from_port = 80
    to_port = 80
    protocol = "tcp"
    cidr_blocks = [
      "24.5.222.73/32", // US OFFICE
      "76.102.161.105/32", // KEKO HOME
      "76.103.237.82/32", // SANCHO HOME
      "73.158.200.161/32", // BRANDON HOME
      "83.61.20.90/32", // IGZ CALLAO OFFICE 1
      "83.61.8.95/32",  // IGZ CALLAO OFFICE 2
      "83.56.7.26/32",  // IGZ CALLAO OFFICE 3
      "52.51.50.68/32", // IGZ VPN
      "54.73.0.183/32", // IGZ GITLAB RUNNERS
      "216.194.50.82/32", // Brian Sullivan's IP
      "216.194.28.12/32", // Joseph Degeorge's IP
      "216.194.50.83/32",  // MetTel Office IP
      "216.194.28.132/32", // MetTel Office IP
      "216.194.28.130/32",  // MetTel Cisco VPN
      "216.194.28.16/32" // MetTel Fortinet VPN     
    ]
  }

  ingress {
    from_port = 8
    to_port = 0
    protocol = "icmp"
    cidr_blocks = [
      "0.0.0.0/0"]
  }

  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = [
      "0.0.0.0/0"]
  }

  tags = {
    Name = local.automation-dev-inbound-security_group-tag-Name
    Environment = var.ENVIRONMENT
  }
}

data "aws_acm_certificate" "automation" {
  domain = "*.mettel-automation.net"
  most_recent = true
}

resource "aws_lb" "automation-alb" {
  name = var.ENVIRONMENT
  load_balancer_type = "application"
  subnets = data.aws_subnet_ids.mettel-automation-public-subnets.ids
  security_groups = [
    aws_security_group.automation-dev-inbound.id]

  tags = {
    Name = var.ENVIRONMENT
    Environment = var.ENVIRONMENT
  }

  timeouts {
    create = "15m"
    update = "15m"
  }
}

resource "aws_lb_listener" "front_end" {
  load_balancer_arn = aws_lb.automation-alb.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }

  }
}

resource "aws_lb_target_group" "automation-front_end" {
  name = "${var.ENVIRONMENT}-frontend"
  port = 80
  protocol = "HTTP"
  vpc_id = data.aws_vpc.mettel-automation-vpc.id
  target_type = "ip"
  stickiness {
    type = "lb_cookie"
    enabled = false
  }

  depends_on = [ "aws_lb.automation-alb" ]

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name = local.automation-front_end-lb_target_group-tag-Name
    Environment = var.ENVIRONMENT
  }
}

// grafana configuration for ALB
resource "aws_lb_listener" "automation-grafana" {
  load_balancer_arn = aws_lb.automation-alb.arn
  port = "443"
  protocol = "HTTPS"
  certificate_arn = data.aws_acm_certificate.automation.arn

  default_action {
    target_group_arn = aws_lb_target_group.automation-metrics-grafana.arn
    type = "forward"
  }
}

resource "aws_lb_target_group" "automation-metrics-grafana" {
  name = local.automation-metrics-grafana-target_group-name
  port = 3000
  protocol = "HTTP"
  vpc_id = data.aws_vpc.mettel-automation-vpc.id
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
    interval            = 90
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

// dispatch-portal configuration for ALB
resource "aws_lb_target_group" "automation-dispatch-portal" {
  name = local.automation-dispatch-portal-target_group-name
  port = 8080
  protocol = "HTTP"
  vpc_id = data.aws_vpc.mettel-automation-vpc.id
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

// email-tagger-monitor configuration for ALB
resource "aws_lb_target_group" "automation-email-tagger-monitor" {
  name = local.automation-email-tagger-monitor-target_group-name
  port = 5000
  protocol = "HTTP"
  vpc_id = data.aws_vpc.mettel-automation-vpc.id
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
    port                = 5000
    matcher             = 200
    protocol            = "HTTP"
    path                = "/_health"
  }

  tags = {
    Name = local.automation-email-tagger-monitor-target_group-tag-Name
    Environment = var.ENVIRONMENT
  }

}

resource "aws_alb_listener_rule" "automation-email-tagger-monitor-path" {
  depends_on   = [ aws_lb_target_group.automation-email-tagger-monitor ]
  listener_arn = aws_lb_listener.automation-grafana.arn
  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.automation-email-tagger-monitor.arn
  }
  condition {
    path_pattern {
      values = local.automation-email-tagger-monitor-alb-listener-rules
    }
  }
}

// ticket-statistics configuration for ALB
resource "aws_lb_target_group" "automation-ticket-statistics" {
  name = local.automation-ticket-statistics-target_group-name
  port = 5000
  protocol = "HTTP"
  vpc_id = data.aws_vpc.mettel-automation-vpc.id
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
    port                = 5000
    matcher             = 200
    protocol            = "HTTP"
    path                = "/_health"
  }

  tags = {
    Name = local.automation-ticket-statistics-target_group-tag-Name
    Environment = var.ENVIRONMENT
  }

}

resource "aws_alb_listener_rule" "automation-ticket-statistics-path" {
  depends_on   = [ aws_lb_target_group.automation-ticket-statistics ]
  listener_arn = aws_lb_listener.automation-grafana.arn
  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.automation-ticket-statistics.arn
  }
  condition {
    path_pattern {
      values = [
        "/api/statistics/*",
        "/api/statistics"]
    }
  }
}
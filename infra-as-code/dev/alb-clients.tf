###################################
###   O'Reilly public endpoint  ###
###################################

resource "aws_route53_record" "oreilly" {
  count = var.CURRENT_ENVIRONMENT == "production" ? 1 : 0
  zone_id = data.aws_route53_zone.automation.zone_id
  name = var.CURRENT_ENVIRONMENT == "dev" ? "oreilly-${local.automation-route53_record-name}" : "oreilly.${data.aws_route53_zone.automation.name}"
  type = "A"

  alias {
    name = aws_lb.automation-oreilly-alb[0].dns_name
    zone_id = aws_lb.automation-oreilly-alb[0].zone_id
    evaluate_target_health = true
  }
}

resource "aws_security_group" "automation-dev-oreilly-inbound" {
  count = var.CURRENT_ENVIRONMENT == "production" ? 1 : 0
  name = "${var.ENVIRONMENT}-oreilly-inbound"
  description = "Allowed connections into oreilly ALB"
  vpc_id = data.aws_vpc.mettel-automation-vpc.id

  lifecycle {
    create_before_destroy = true
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
    Name = "${var.ENVIRONMENT}-oreilly-inbound"
    Environment = var.ENVIRONMENT
  }
}

resource "aws_lb" "automation-oreilly-alb" {
  count = var.CURRENT_ENVIRONMENT == "production" ? 1 : 0
  name = "${var.ENVIRONMENT}-oreilly"
  load_balancer_type = "application"
  subnets = data.aws_subnet_ids.mettel-automation-public-subnets.ids
  security_groups = [
    aws_security_group.automation-dev-oreilly-inbound[0].id]

  tags = {
    Name = "${var.ENVIRONMENT}-oreilly"
    Environment = var.ENVIRONMENT
  }

  timeouts {
    create = "15m"
    update = "15m"
  }
}

resource "aws_lb_listener" "oreilly_front_end" {
  count = var.CURRENT_ENVIRONMENT == "production" ? 1 : 0
  load_balancer_arn = aws_lb.automation-oreilly-alb[0].arn
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

resource "aws_lb_target_group" "target_group_oreilly_fornt_end" {
  count = var.CURRENT_ENVIRONMENT == "production" ? 1 : 0
  name = "${var.ENVIRONMENT}-oreilly-frontend"
  port = 80
  protocol = "HTTP"
  vpc_id = data.aws_vpc.mettel-automation-vpc.id
  target_type = "ip"
  stickiness {
    type = "lb_cookie"
    enabled = false
  }

  depends_on = [ "aws_lb.automation-oreilly-alb[0]" ]

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name = "${var.ENVIRONMENT}-oreilly-frontend"
    Environment = var.ENVIRONMENT
  }
}

resource "aws_lb_listener" "oreilly_front_end_ssl" {
  count = var.CURRENT_ENVIRONMENT == "production" ? 1 : 0
  load_balancer_arn = aws_lb.automation-oreilly-alb[0].arn
  port = "443"
  protocol = "HTTPS"
  certificate_arn = data.aws_acm_certificate.automation.arn

  default_action {
    target_group_arn = aws_lb_target_group.target_group_oreilly_front_end_ssl[0].arn
    type = "forward"
  }
}

resource "aws_lb_target_group" "target_group_oreilly_front_end_ssl" {
  count = var.CURRENT_ENVIRONMENT == "production" ? 1 : 0
  name = "${var.ENVIRONMENT}-oreilly-frontend-ssl"
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
    interval            = 90
    port                = 5000
    matcher             = 200
    protocol            = "HTTP"
    path                = "/_health"
  }

  tags = {
    Name = "${var.ENVIRONMENT}-oreilly-frontend-ssl"
    Environment = var.ENVIRONMENT
  }

}

resource "aws_alb_listener_rule" "oreilly_front_end_ssl_path" {
  count = var.CURRENT_ENVIRONMENT == "production" ? 1 : 0
  depends_on   = [ aws_lb_target_group.target_group_oreilly_front_end_ssl[0] ]
  listener_arn = aws_lb_listener.oreilly_front_end_ssl[0].arn
  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.target_group_oreilly_front_end_ssl[0].arn
  }
  condition {
    path_pattern {
      values = [
        "/api/metrics/*",
        "/api/metrics"]
    }
  }
}
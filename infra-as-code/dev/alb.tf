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
      "37.134.83.253/32", // XOAN HOME
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
      "37.134.194.81/32", // XOAN HOME
      "79.146.229.176/32",   // JESUS HOME
      "139.47.71.34/32",    // JC HOME
      "54.73.0.183/32", // IGZ GITLAB RUNNERS
      "216.194.50.82/32", // Brian Sullivan's IP
      "216.194.28.12/32", // Joseph Degeorge's IP
      "216.194.50.83/32",  // MetTel Office IP
      "216.194.28.132/32" // MetTel Office IP
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
      "216.194.28.132/32" // MetTel Office IP
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

resource "aws_security_group" "automation-dev-inbound" {
  name = "${var.ENVIRONMENT}-inbound"
  description = "Allowed connections into ALB"
  vpc_id = "${aws_vpc.automation-vpc.id}"

  lifecycle {
    create_before_destroy = true
  }

  ingress {
    from_port = 8222
    to_port = 8222
    protocol = "tcp"
    cidr_blocks = [
      "12.15.242.50/32", // US OFFICE
      "76.102.161.105/32", // KEKO HOME
      "76.103.237.82/32", // SANCHO HOME
      "83.61.20.90/32", // IGZ CALLAO OFFICE 1
      "83.61.8.95/32",  // IGZ CALLAO OFFICE 2
      "83.56.7.26/32",   // IGZ CALLAO OFFICE 3
      "83.40.63.125/32", // XOAN HOME MADRID
      "87.219.160.222/32" // XOAN HOME GALICIA
    ]
  }

  ingress {
    from_port = 443
    to_port = 443
    protocol = "tcp"
    cidr_blocks = [
      "12.15.242.50/32", // US OFFICE
      "76.102.161.105/32", // KEKO HOME
      "76.103.237.82/32", // SANCHO HOME
      "83.61.20.90/32", // IGZ CALLAO OFFICE 1
      "83.61.8.95/32",  // IGZ CALLAO OFFICE 2
      "83.56.7.26/32",  // IGZ CALLAO OFFICE 3
      "83.40.63.125/32", // XOAN HOME MADRID
      "87.219.160.222/32", // XOAN HOME GALICIA
      "54.73.0.183/32", // IGZ GITLAB RUNNERS
      "216.194.50.82/32" // METTEL OFFICE
    ]
  }

    ingress {
    from_port = 80
    to_port = 80
    protocol = "tcp"
    cidr_blocks = [
      "12.15.242.50/32", // US OFFICE
      "76.102.161.105/32", // KEKO HOME
      "76.103.237.82/32", // SANCHO HOME
      "83.61.20.90/32", // IGZ CALLAO OFFICE 1
      "83.61.8.95/32",  // IGZ CALLAO OFFICE 2
      "83.56.7.26/32",  // IGZ CALLAO OFFICE 3
      "83.40.63.125/32", // XOAN HOME MADRID
      "87.219.160.222/32", // XOAN HOME GALICIA
      "54.73.0.183/32", // IGZ GITLAB RUNNERS
      "216.194.50.82/32" // METTEL OFFICE
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
    Name = "${var.ENVIRONMENT}-inbound"
  }
}

data "aws_acm_certificate" "automation" {
  domain = "*.mettel-automation.net"
  most_recent = true
}

resource "aws_lb" "automation-alb" {
  name = "${var.ENVIRONMENT}"
  load_balancer_type = "application"
  subnets = [
    "${aws_subnet.automation-public_subnet-1a.id}",
    "${aws_subnet.automation-public_subnet-1b.id}"]
  security_groups = [
    "${aws_security_group.automation-dev-inbound.id}"]

  tags = {
    Name = "${var.ENVIRONMENT}"
    Environment = "${var.ENVIRONMENT}"
  }
}

resource "aws_lb_listener" "front_end" {
  load_balancer_arn = "${aws_lb.automation-alb.arn}"
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
  vpc_id = "${aws_vpc.automation-vpc.id}"
  target_type = "ip"
  stickiness {
    type = "lb_cookie"
    enabled = false
  }

  depends_on = [
    "aws_lb.automation-alb"]

  lifecycle {
    create_before_destroy = true
  }
}
resource "aws_security_group" "mettel-automation-pro-inbound" {
  name = "${var.environment}-inbound"
  description = "Allow HTTP from Anywhere into ALB"
  vpc_id = "${aws_vpc.mettel-automation-pro-vpc.id}"

  ingress {
    from_port = 80
    to_port = 80
    protocol = "tcp"
    cidr_blocks = [
      "0.0.0.0/0"]
  }

  ingress {
    from_port = 443
    to_port = 443
    protocol = "tcp"
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

  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = [
      "0.0.0.0/0"]
  }

  tags {
    Name = "${var.environment}-inbound"
  }
}

resource "aws_alb" "mettel-automation-pro-alb" {
  name = "${var.environment}"
  subnets = [
    "${aws_subnet.mettel-automation-pro-public_subnet-1a.id}",
    "${aws_subnet.mettel-automation-pro-public_subnet-1b.id}"]
  security_groups = [
    "${aws_security_group.mettel-automation-pro-inbound.id}"]

  tags {
    Name = "${var.environment}"
    Environment = "${var.environment}"
  }
}

resource "aws_alb_listener" "mettel-automation-pro-http" {
  load_balancer_arn = "${aws_alb.mettel-automation-pro-alb.arn}"
  port = "80"
  protocol = "HTTP"

  default_action {
    target_group_arn = "${aws_alb_target_group.mettel-automation-pro-redirector.arn}"
    type = "forward"
  }
}

data "aws_acm_certificate" "targetx" {
  domain = "*.targetx.com"
  most_recent = true
}

resource "aws_alb_listener" "mettel-automation-pro-https" {
  load_balancer_arn = "${aws_alb.mettel-automation-pro-alb.arn}"
  port = "443"
  protocol = "HTTPS"
  ssl_policy = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn = "${data.aws_acm_certificate.targetx.arn}"

  default_action {
    target_group_arn = "${aws_alb_target_group.mettel-automation-pro-frontend.arn}"
    type = "forward"
  }
}

resource "aws_alb_listener_rule" "api" {
  listener_arn = "${aws_alb_listener.mettel-automation-pro-https.arn}"
  priority = 100

  action {
    type = "forward"
    target_group_arn = "${aws_alb_target_group.mettel-automation-pro-backend.arn}"
  }

  condition {
    field = "path-pattern"
    values = [
      "/api/*"]
  }
}

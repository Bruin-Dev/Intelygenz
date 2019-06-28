resource "aws_security_group" "automation-inbound" {
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
      "67.169.23.168/32", // KEKO HOME
      "76.103.237.82/32" // SANCHO HOME
    ]
  }

  ingress {
    from_port = 3000
    to_port = 3000
    protocol = "tcp"
    cidr_blocks = [
      "12.15.242.50/32", // US OFFICE
      "67.169.23.168/32", // KEKO HOME
      "76.103.237.82/32" // SANCHO HOME
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

resource "aws_alb" "automation-alb" {
  name = "${var.ENVIRONMENT}"
  subnets = [
    "${aws_subnet.automation-public_subnet-1a.id}",
    "${aws_subnet.automation-public_subnet-1b.id}"]
  security_groups = [
    "${aws_security_group.automation-inbound.id}"]

  tags = {
    Name = "${var.ENVIRONMENT}"
    Environment = "${var.ENVIRONMENT}"
  }
}

//resource "aws_lb_listener" "front_end" {
//  load_balancer_arn = "${aws_alb.automation-alb.arn}"
//  port              = "80"
//  protocol          = "HTTP"
//
//  default_action {
//    type = "redirect"
//
//    redirect {
//      port        = "443"
//      protocol    = "HTTPS"
//      status_code = "HTTP_301"
//    }
//  }
//}
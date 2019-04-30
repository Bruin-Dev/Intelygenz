resource "aws_security_group" "insights-dev-inbound" {
  name = "${var.environment}-inbound"
  description = "Allowed connections into ALB"
  vpc_id = "${aws_vpc.automation-vpc.id}"

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
    from_port = 8222
    to_port = 8222
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

resource "aws_alb" "insights-dev-alb" {
  name = "${var.environment}"
  subnets = [
    "${aws_subnet.automation-public_subnet-1a.id}",
    "${aws_subnet.automation-public_subnet-1b.id}"]
  security_groups = [
    "${aws_security_group.insights-dev-inbound.id}"]

  tags {
    Name = "${var.environment}"
    Environment = "${var.environment}"
  }
}

resource "aws_alb_listener" "grafana" {
  load_balancer_arn = "${aws_alb.insights-dev-alb.arn}"
  port = "8222"
  protocol = "TCP"

  default_action {
    target_group_arn = "${aws_alb_target_group.automation-nats-server.arn}"
    type = "forward"
  }
}
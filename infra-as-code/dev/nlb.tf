resource "aws_lb" "automation-nlb" {
  name               = local.automation-nlb-name
  internal           = false
  load_balancer_type = "network"
    subnets = [
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1a.id,
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1b.id]

  enable_deletion_protection = false

  tags = {
    Name        = local.automation-nlb-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_lb_listener" "automation-thanos-store-gateway" {
  load_balancer_arn = aws_lb.automation-nlb.arn
  port = "10901"
  protocol = "TCP"

  default_action {
    target_group_arn = aws_lb_target_group.automation-thanos-store-gateway.arn
    type = "forward"
  }
}

resource "aws_lb_target_group" "automation-thanos-store-gateway" {
  name = local.automation-metrics-thanos-store-gateway-target_group-name
  port = 10901
  protocol = "TCP"
  vpc_id = data.terraform_remote_state.tfstate-network-resources.outputs.vpc_automation_id
  target_type = "ip"

  depends_on = [
    "aws_lb.automation-nlb"]

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name = local.automation-metrics-thanos-store-gateway-target_group-tag-Name
    Environment = var.ENVIRONMENT
  }

}
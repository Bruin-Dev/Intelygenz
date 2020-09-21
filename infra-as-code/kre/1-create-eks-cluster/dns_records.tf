resource "aws_route53_record" "kre_ns" {
  allow_overwrite = true
  name            = local.kre_record_hosted_zone_name
  ttl             = 300
  type            = "NS"
  zone_id         = data.aws_route53_zone.mettel_automation.zone_id

  records = [
    aws_route53_zone.kre_hosted_zone.name_servers[0],
    aws_route53_zone.kre_hosted_zone.name_servers[1],
    aws_route53_zone.kre_hosted_zone.name_servers[2],
    aws_route53_zone.kre_hosted_zone.name_servers[3],
  ]
}

/*
resource "aws_route53_record" "kre_record_alias" {
  zone_id = aws_route53_zone.kre_hosted_zone.zone_id
  name    = "*.kre-${var.CURRENT_ENVIRONMENT}.mettel-automation.net"
  type    = "A"
  records = [aws_eip.elb_ingress_ip.public_ip]
}

resource "aws_eip" "elb_ingress_ip" {
  tags = {
    Environment  = terraform.workspace
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
  }
}*/

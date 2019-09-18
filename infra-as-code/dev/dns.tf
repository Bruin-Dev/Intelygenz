data "aws_route53_zone" "automation" {
  name = "mettel-automation.net."
}

resource "aws_route53_record" "automation" {
  zone_id = data.aws_route53_zone.automation.zone_id
  name = local.automation-route53_record-name
  type = "A"

  alias {
    name = aws_lb.automation-alb.dns_name
    zone_id = aws_lb.automation-alb.zone_id
    evaluate_target_health = true
  }
}

resource "aws_service_discovery_private_dns_namespace" "automation-zone" {
  name        = local.automation-zone-service_discovery_private_dns-name
  description = "private DNS zone for automation"
  vpc         = aws_vpc.automation-vpc.id
}

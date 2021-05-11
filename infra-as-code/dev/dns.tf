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
  vpc         = data.aws_vpc.mettel-automation-vpc.id
}

# email-tagger public endpoint
resource "aws_route53_record" "email-tagger" {
  zone_id = data.aws_route53_zone.automation.zone_id
  name = var.CURRENT_ENVIRONMENT == "dev" ? "email-tagger-${local.automation-route53_record-name}" : "email-tagger.${data.aws_route53_zone.automation.name}"
  type = "A"

  alias {
    name = aws_lb.automation-alb.dns_name
    zone_id = aws_lb.automation-alb.zone_id
    evaluate_target_health = true
  }
}

// Hosted zone local variables
locals {
  kre_base_domain_name = var.CURRENT_ENVIRONMENT == "dev" ? "${var.RUNTIME_NAME}-${var.CURRENT_ENVIRONMENT}.${local.hosted_zone_name}" : "${var.RUNTIME_NAME}.${local.hosted_zone_name}"
}

resource "aws_route53_zone" "kre_hosted_zone" {
  name = local.kre_base_domain_name
}

resource "aws_route53_record" "kre_ns" {
  allow_overwrite = true
  name            = local.kre_base_domain_name
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
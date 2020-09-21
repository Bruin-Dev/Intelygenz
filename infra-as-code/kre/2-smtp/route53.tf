resource "aws_route53_zone" "temp_domain" {
  name = local.temp_domain
}

resource "aws_route53_record" "temp_domain_ns_records" {
  zone_id = data.aws_route53_zone.mettel_automation.zone_id
  name    = local.temp_domain
  type    = "NS"
  ttl     = "30"

  records = aws_route53_zone.temp_domain.name_servers
}

resource "aws_route53_record" "temp_spf" {
  count   = var.enable_spf_record ? 0 : 1
  zone_id = aws_route53_zone.temp_domain.zone_id
  name    = local.temp_domain
  type    = "TXT"
  ttl     = "600"
  records = ["v=spf1 include:_spf.google.com include:servers.mcsv.net ~all"]
}

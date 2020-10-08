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

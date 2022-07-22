module "docs_s3_website" {
  source           = "./modules/s3-website"
  prefix           = "s3docs"
  region           = data.aws_region.current.name
  environment      = var.CURRENT_ENVIRONMENT
  index_document   = "index.html"
  error_document   = "404.html"
  referer_header   = "mettel-automation-docs"
  logs_buckets     = data.aws_s3_bucket.bucket_logs.bucket_domain_name
  ssl_certificate  = data.aws_acm_certificate.mettel_automation_certificate.arn
  domain_name      = [local.logs_dns_name]

  vpn_remote_ipset = [
    {
      value = "52.51.50.68/32" # VPN igz
      type  = "IPV4"
    },
  ]
}

resource "aws_route53_record" "docs_s3_website" {
  zone_id = data.aws_route53_zone.mettel_automation.zone_id
  name = local.logs_dns_name
  type = "A"
  alias {
    name                   = module.docs_s3_website.cloudfront_endpoint
    zone_id                = module.docs_s3_website.cloudfront_zoneid
    evaluate_target_health = false
  }
}
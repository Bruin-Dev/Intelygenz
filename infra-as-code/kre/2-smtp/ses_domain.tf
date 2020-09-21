module "ses_domain" {
  source = "trussworks/ses-domain/aws"

  domain_name     = local.temp_domain
  route53_zone_id = aws_route53_zone.temp_domain.zone_id

  from_addresses   = ["no-reply@${local.temp_domain}"]
  mail_from_domain = "email.${local.temp_domain}"

  dmarc_rua = "mettel_dmarc@intelygenz.mettel-automation.net"

  receive_s3_bucket = aws_s3_bucket.temp_bucket.id
  receive_s3_prefix = local.ses_bucket_prefix
  enable_spf_record = var.enable_spf_record
  extra_ses_records = var.extra_ses_records

  ses_rule_set = aws_ses_receipt_rule_set.main.rule_set_name

  version = "3.0.0"
}

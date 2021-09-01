#######################################
### Create CERT and dns resources for VALIDATE it and avoid to do manual steps

resource "aws_acm_certificate" "ssl_certificate" {
  domain_name               = "*.mettel-automation.net"
  validation_method         = "DNS"

  tags = {
    Name        = "SSL Certificate us-east-1"
    Environment  = var.CURRENT_ENVIRONMENT
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Creates route 53 records for validation of DNS
resource "aws_route53_record" "ssl_certificate_dns_validation" {
  for_each = {
    for dvo in aws_acm_certificate.ssl_certificate.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = data.aws_route53_zone.mettel_automation.zone_id
}

# Validates the ACM certificate
resource "aws_acm_certificate_validation" "cert_validation_ssl_certificate" {
  # api-gateway / cloudfront certificates need to use the us-east-1 region
  certificate_arn         = aws_acm_certificate.ssl_certificate.arn
  validation_record_fqdns = [for record in aws_route53_record.ssl_certificate_dns_validation : record.fqdn]
}

### end CERT and VALIDATION
#######################################
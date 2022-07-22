## Cloudfront taking files from private bucket
resource "aws_cloudfront_origin_access_identity" "access_identity_website" {
  comment = "${var.prefix}-identity-for-cloudfront-to-access-s3-bucket-${var.environment}"
}

locals {
  s3_origin_id = "${var.prefix}-origin-${var.environment}"
}

# Cloudfront
resource "aws_cloudfront_distribution" "s3_distribution_website" {
  origin {
    domain_name = aws_s3_bucket.s3_bucket_website.website_endpoint
    origin_id   = local.s3_origin_id
    connection_attempts = 3
    connection_timeout  = 10
    custom_origin_config {
      http_port                = 80
      https_port               = 443
      origin_keepalive_timeout = 5
      origin_protocol_policy   = "http-only"
      origin_read_timeout      = 30
      origin_ssl_protocols     = ["TLSv1", "TLSv1.1", "TLSv1.2"]
    }
    custom_header {
      name  = "Referer"
      value = var.referer_header
    }
  }

  enabled             = true
  is_ipv6_enabled     = true
  comment             = "${var.prefix}-website-${var.environment}-distribution"
  default_root_object = var.index_document
  logging_config {
    include_cookies = false
    bucket          = var.logs_buckets
    prefix          = "${var.environment}/cloudfront/${var.prefix}-website"
  }

  aliases    = var.domain_name
  web_acl_id  = aws_waf_web_acl.waf.id
  
  custom_error_response {
      error_caching_min_ttl = 0
      error_code            = 403
      response_code         = 200
      response_page_path    = "/${var.error_document}"
  }
  custom_error_response {
      error_caching_min_ttl = 0
      error_code            = 404
      response_code         = 200
      response_page_path    = "/${var.error_document}"
  }

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = local.s3_origin_id

  forwarded_values {
    query_string = false
    #headers      = ["Origin", "Access-Control-Request-Headers", "Access-Control-Request-Method", "Accept", "Content-Type"]

    cookies {
      forward = "none"
    }
  }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 0
  }

  price_class = "PriceClass_100"

  tags = {
    environment = var.environment
    name        = local.s3_origin_id
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn      = var.ssl_certificate
    minimum_protocol_version = "TLSv1"
    ssl_support_method       = "sni-only"
  }

  depends_on = [
    aws_waf_web_acl.waf
  ]
}

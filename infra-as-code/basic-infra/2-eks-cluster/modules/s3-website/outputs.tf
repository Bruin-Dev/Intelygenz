#
# Outputs
#

output "cloudfront_endpoint" {
  value = aws_cloudfront_distribution.s3_distribution_website.domain_name
}

output "cloudfront_zoneid" {
  value = aws_cloudfront_distribution.s3_distribution_website.hosted_zone_id
}
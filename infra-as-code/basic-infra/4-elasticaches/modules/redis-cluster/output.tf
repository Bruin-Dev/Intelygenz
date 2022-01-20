output "REDIS_HOSTNAME" {
  description = "Hostname of Redis"
  value = aws_route53_record.automation-redis-private-name.fqdn
}
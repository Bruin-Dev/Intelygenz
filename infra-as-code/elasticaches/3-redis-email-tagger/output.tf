output "REDIS_EMAIL_TAGGER_HOSTNAME" {
  description = "Hostname of Redis email-tagger"
  value = module.redis-email-tagger.REDIS_HOSTNAME
}
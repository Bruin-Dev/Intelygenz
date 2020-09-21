# SES only allows one (just like Highlander and Lord of the Rings) rule set to
# be active at any point in time. So this will live in the app-global state file.
locals {
  ses_bucket_prefix       = "ses"
  infra_test_truss_coffee = "infra-test.truss.coffee"
  temp_domain             = "${var.subdomain_name_prefix}.${data.aws_route53_zone.mettel_automation.name}"
  ses_bucket_name = "${var.common_info.project}-${var.CURRENT_ENVIRONMENT}-smtp"
}

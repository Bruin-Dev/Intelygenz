# mettel-automation hosted zone info
data "aws_route53_zone" "mettel_automation" {
  name         = "mettel-automation.net."
  private_zone = false
}

data "aws_caller_identity" "current" {}
data "aws_iam_account_alias" "current" {}
data "aws_partition" "current" {}

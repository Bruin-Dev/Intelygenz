resource "aws_route53_zone" "kre_hosted_zone" {
  name = "kre-${var.CURRENT_ENVIRONMENT}.mettel-automation.net"

  depends_on = [module.mettel-automation-eks-cluster]
}

locals {
  // EKS cluster local variables
  eks_cluster_name                = var.CURRENT_ENVIRONMENT == "dev" ? "${var.common_info.project}-${var.CURRENT_ENVIRONMENT}" : var.common_info.project

  // Hosted zone local variables
  hosted_zone_name = "mettel-automation.net"
}
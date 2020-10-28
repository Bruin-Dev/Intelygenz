locals {
  bucket_name = var.CURRENT_ENVIRONMENT == "dev" ? "${var.common_info.project}-${var.CURRENT_ENVIRONMENT}-eks" : "${var.common_info.project}-eks"
}

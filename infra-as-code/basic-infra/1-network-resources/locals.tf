locals {
  // automation-vpc local vars
  automation-vpc-tag-Name = "mettel-automation-vpc-${var.CURRENT_ENVIRONMENT}"
  automation-nat_eip-1a-tag-Name = "mettel-automation-eip-1a-${var.CURRENT_ENVIRONMENT}"
  automation-nat_eip-1b-tag-Name = "mettel-automation-eip-1b-${var.CURRENT_ENVIRONMENT}"
  automation-internet_gateway-tag-Name = "mettel-automation-internet_gateway-${var.CURRENT_ENVIRONMENT}"
  automation-nat_gateway-1a-tag-Name = "mettel-automation-nat_gateway-1a-${var.CURRENT_ENVIRONMENT}"
  automation-nat_gateway-1b-tag-Name = "mettel-automation-nat_gateway-1b-${var.CURRENT_ENVIRONMENT}"
  automation-public_subnet-1a-tag-Name = "mettel-automation-public-subnet-1a-${var.CURRENT_ENVIRONMENT}"
  automation-public_subnet-1b-tag-Name = "mettel-automation-public-subnet-1b-${var.CURRENT_ENVIRONMENT}"
  automation-private_subnet-1a-tag-Name = "mettel-automation-private-subnet-1a-${var.CURRENT_ENVIRONMENT}"
  automation-private_subnet-1b-tag-Name = "mettel-automation-private-subnet-1b-${var.CURRENT_ENVIRONMENT}"
  automation-private-route_table-1a-tag-Name = "mettel-automation-private-route-table-1a-${var.CURRENT_ENVIRONMENT}"
  automation-private-route_table-1b-tag-Name = "mettel-automation-private-route-table-1b-${var.CURRENT_ENVIRONMENT}"
  automation-public-route_table-1a-tag-Name = "mettel-automation-public-route-table-1a-${var.CURRENT_ENVIRONMENT}"
  automation-public-route_table-1b-tag-Name = "mettel-automation-public-route-table-1b-${var.CURRENT_ENVIRONMENT}"
  automation-default-security-group-name = "mettel-automation-default-sg-${var.CURRENT_ENVIRONMENT}"
  automation-default-security_group-tag-Name = "mettel-automation-default-${var.CURRENT_ENVIRONMENT}"

  // virtual private gateway local vars
  virtual-private-gateway-tag-Name = var.CURRENT_ENVIRONMENT == "dev" ? "${var.common_info.project}-${var.CURRENT_ENVIRONMENT}-vpg" : "${var.common_info.project}-vpg"

  // Direct Connect way created and managed by MetTel's Network department
  direct-connect-gateway-name = "Corporate-DC-GW"

  eks_tags = var.CURRENT_ENVIRONMENT == "dev" ? {
    format("kubernetes.io/cluster/%s-dev", var.EKS_KRE_BASE_NAME) = "shared",
    format("kubernetes.io/cluster/%s-dev", var.EKS_PROJECT_BASE_NAME) = "shared"
  }: {
    format("kubernetes.io/cluster/%s", var.EKS_KRE_BASE_NAME) = "shared",
    format("kubernetes.io/cluster/%s", var.EKS_PROJECT_BASE_NAME) = "shared"
  }
}
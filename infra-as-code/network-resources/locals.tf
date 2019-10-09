locals {
  // automation-vpc local vars
  automation-vpc-tag-Name = "mettel-automation-vpc-${var.NETWORK_ENVIRONMENT}"
  automation-nat_eip-1a-tag-Name = "mettel-automation-eip-1a-${var.NETWORK_ENVIRONMENT}"
  automation-nat_eip-1b-tag-Name = "mettel-automation-eip-1b-${var.NETWORK_ENVIRONMENT}"
  automation-internet_gateway-tag-Name = "mettel-automation-internet_gateway-${var.NETWORK_ENVIRONMENT}"
  automation-nat_gateway-1a-tag-Name = "mettel-automation-nat_gateway-1a-${var.NETWORK_ENVIRONMENT}"
  automation-nat_gateway-1b-tag-Name = "mettel-automation-nat_gateway-1b-${var.NETWORK_ENVIRONMENT}"
  automation-public_subnet-1a-tag-Name = "mettel-automation-public-subnet-1a-${var.NETWORK_ENVIRONMENT}"
  automation-public_subnet-1b-tag-Name = "mettel-automation-public-subnet-1b-${var.NETWORK_ENVIRONMENT}"
  automation-private_subnet-1a-tag-Name = "mettel-automation-private-subnet-1a-${var.NETWORK_ENVIRONMENT}"
  automation-private_subnet-1b-tag-Name = "mettel-automation-private-subnet-1b-${var.NETWORK_ENVIRONMENT}"
  automation-private-route_table-1a-tag-Name = "mettel-automation-private-route-table-1a-${var.NETWORK_ENVIRONMENT}"
  automation-private-route_table-1b-tag-Name = "mettel-automation-private-route-table-1b-${var.NETWORK_ENVIRONMENT}"
  automation-public-route_table-tag-Name = "mettel-automation-public-route-table-1a-${var.NETWORK_ENVIRONMENT}"
  automation-default-security-group-name = "mettel-automation-default-sg-${var.NETWORK_ENVIRONMENT}"
  automation-default-security_group-tag-Name = "mettel-automation-default-${var.NETWORK_ENVIRONMENT}"
}
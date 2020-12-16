resource "aws_vpn_gateway" "vpn_gw" {
  vpc_id = aws_vpc.automation-vpc.id

  tags = {
    Name = local.virtual-private-gateway-tag-Name
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
    Environment  = var.CURRENT_ENVIRONMENT
  }
}

resource "aws_dx_gateway_association" "direct-connect-gateway-vpg-association" {
  dx_gateway_id         = data.aws_dx_gateway.direct-connect-gateway.id
  associated_gateway_id = aws_vpn_gateway.vpn_gw.id

  allowed_prefixes = [
    var.cdir_private_1[var.CURRENT_ENVIRONMENT],
    var.cdir_private_2[var.CURRENT_ENVIRONMENT],
  ]
}
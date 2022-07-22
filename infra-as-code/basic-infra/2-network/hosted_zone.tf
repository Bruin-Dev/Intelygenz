# private zone for cluster resources
resource "aws_route53_zone" "automation-private-zone" {
  name = local.automation-private-zone-Name

  vpc {
    vpc_id = aws_vpc.automation-vpc.id
  }

  tags = {
    Name         = local.automation-private-zone-tag-Name
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
  }
}
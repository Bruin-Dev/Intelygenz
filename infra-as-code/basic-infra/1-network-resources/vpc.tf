/*====
The VPC
======*/

resource "aws_vpc" "automation-vpc" {
  cidr_block = var.cidr_base[var.CURRENT_ENVIRONMENT]
  enable_dns_hostnames = true
  enable_dns_support = true

  tags = {
    Name         = local.automation-vpc-tag-Name
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
  }
}

/*====
Subnets
======*/
/* Internet gateway for the public subnet */
resource "aws_internet_gateway" "automation-igw" {
  vpc_id = aws_vpc.automation-vpc.id

  tags = {
    Name         = local.automation-internet_gateway-tag-Name
    Environment  = var.CURRENT_ENVIRONMENT
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
  }
}


/* Elastic IP for NAT */
resource "aws_eip" "automation-nat_eip-1a" {
  vpc = true
  tags = {
    Name         = local.automation-nat_eip-1a-tag-Name
    Environment  = var.CURRENT_ENVIRONMENT
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
  }
}

resource "aws_eip" "automation-nat_eip-1b" {
  vpc = true
  tags = {
    Name         = local.automation-nat_eip-1b-tag-Name
    Environment  = var.CURRENT_ENVIRONMENT
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
  }
}

/* NAT */
resource "aws_nat_gateway" "automation-nat-1a" {
  allocation_id = aws_eip.automation-nat_eip-1a.id
  subnet_id = aws_subnet.automation-public_subnet-1a.id

  tags = {
    Name         = local.automation-nat_gateway-1a-tag-Name
    Environment  = var.CURRENT_ENVIRONMENT
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
  }
}

resource "aws_nat_gateway" "automation-nat-1b" {
  allocation_id = aws_eip.automation-nat_eip-1b.id
  subnet_id = aws_subnet.automation-public_subnet-1b.id

  tags = {
    Name         = local.automation-nat_gateway-1b-tag-Name
    Environment  = var.CURRENT_ENVIRONMENT
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
  }
}

/* Public subnet */
resource "aws_subnet" "automation-public_subnet-1a" {
  vpc_id = aws_vpc.automation-vpc.id
  cidr_block = var.cdir_public_1[var.CURRENT_ENVIRONMENT]
  availability_zone = "us-east-1a"
  map_public_ip_on_launch = true

  tags = merge(local.eks_tags, {
    Name                      = local.automation-public_subnet-1a-tag-Name
    "kubernetes.io/role/elb"  = ""
    Environment               = var.CURRENT_ENVIRONMENT
    Project                   = var.common_info.project
    Provisioning              = var.common_info.provisioning
    Type                      = "Public"
  })
}

resource "aws_subnet" "automation-public_subnet-1b" {
  vpc_id = aws_vpc.automation-vpc.id
  cidr_block = var.cdir_public_2[var.CURRENT_ENVIRONMENT]
  availability_zone = "us-east-1b"
  map_public_ip_on_launch = true

  tags = merge(local.eks_tags, {
    Name                     = local.automation-public_subnet-1b-tag-Name
    "kubernetes.io/role/elb" = ""
    Environment              = var.CURRENT_ENVIRONMENT
    Project                  = var.common_info.project
    Provisioning             = var.common_info.provisioning
    Type                     = "Public"
  })
}

/* Private subnet */
resource "aws_subnet" "automation-private_subnet-1a" {
  vpc_id = aws_vpc.automation-vpc.id
  cidr_block = var.cdir_private_1[var.CURRENT_ENVIRONMENT]
  availability_zone = "us-east-1a"
  map_public_ip_on_launch = false

  tags = merge(local.eks_tags, {
    Name         = local.automation-private_subnet-1a-tag-Name
    Environment  = var.CURRENT_ENVIRONMENT
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
    Type         = "Private"
  })
}

resource "aws_subnet" "automation-private_subnet-1b" {
  vpc_id = aws_vpc.automation-vpc.id
  cidr_block = var.cdir_private_2[var.CURRENT_ENVIRONMENT]
  availability_zone = "us-east-1b"
  map_public_ip_on_launch = false

  tags = merge(local.eks_tags, {
    Name = local.automation-private_subnet-1b-tag-Name
    Environment  = var.CURRENT_ENVIRONMENT
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
    Type         = "Private"
  })
}

/* Routing table for private subnets */
resource "aws_route_table" "automation-private-1a" {
  vpc_id = aws_vpc.automation-vpc.id

  propagating_vgws = [
    aws_vpn_gateway.vpn_gw.id
  ]

  tags = {
    Name = local.automation-private-route_table-1a-tag-Name
    Environment  = var.CURRENT_ENVIRONMENT
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
  }
}

resource "aws_route_table" "automation-private-1b" {
  vpc_id = aws_vpc.automation-vpc.id

  propagating_vgws = [
    aws_vpn_gateway.vpn_gw.id
  ]

  tags = {
    Name = local.automation-private-route_table-1b-tag-Name
    Environment  = var.CURRENT_ENVIRONMENT
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
  }
}

/* Routing table for public subnet */
resource "aws_route_table" "automation-public-1a" {
  vpc_id = aws_vpc.automation-vpc.id

  propagating_vgws = [
    aws_vpn_gateway.vpn_gw.id
  ]

  tags = {
    Name = local.automation-public-route_table-1a-tag-Name
    Environment  = var.CURRENT_ENVIRONMENT
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
  }
}

resource "aws_route_table" "automation-public-1b" {
  vpc_id = aws_vpc.automation-vpc.id

  propagating_vgws = [
    aws_vpn_gateway.vpn_gw.id
  ]

  tags = {
    Name = local.automation-public-route_table-1b-tag-Name
    Environment  = var.CURRENT_ENVIRONMENT
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
  }
}

resource "aws_route" "automation-igw-public-1a" {
  route_table_id = aws_route_table.automation-public-1a.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id = aws_internet_gateway.automation-igw.id
}

resource "aws_route" "automation-igw-public-1b" {
  route_table_id = aws_route_table.automation-public-1b.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id = aws_internet_gateway.automation-igw.id
}

resource "aws_route" "automation-nat-private-1a" {
  route_table_id = aws_route_table.automation-private-1a.id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id = aws_nat_gateway.automation-nat-1a.id
}

resource "aws_route" "automation-nat-private-1b" {
  route_table_id = aws_route_table.automation-private-1b.id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id = aws_nat_gateway.automation-nat-1b.id
}

/* Route table associations */
resource "aws_route_table_association" "automation-public-1a" {
  subnet_id = aws_subnet.automation-public_subnet-1a.id
  route_table_id = aws_route_table.automation-public-1a.id
}

resource "aws_route_table_association" "automation-public-1b" {
  subnet_id = aws_subnet.automation-public_subnet-1b.id
  route_table_id = aws_route_table.automation-public-1b.id
}

resource "aws_route_table_association" "automation-private-1a" {
  subnet_id = aws_subnet.automation-private_subnet-1a.id
  route_table_id = aws_route_table.automation-private-1a.id
}

resource "aws_route_table_association" "automation-private-1b" {
  subnet_id = aws_subnet.automation-private_subnet-1b.id
  route_table_id = aws_route_table.automation-private-1b .id
}

/*====
VPC's Default Security Group
======*/
resource "aws_security_group" "automation-default" {
  name = local.automation-default-security-group-name
  description = "Default security group to allow inbound/outbound from the VPC"
  vpc_id = aws_vpc.automation-vpc.id

  ingress {
    from_port = "0"
    to_port = "0"
    protocol = "-1"
    self = true
  }

  egress {
    from_port = "0"
    to_port = "0"
    protocol = "-1"
    self = "true"
  }

  tags = {
    Name         = local.automation-default-security_group-tag-Name
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
  }
}


#######################
# DATA HIGHWAY ROUTES #
#######################
data "aws_vpc_peering_connection" "data-highway-peering-connection" {
  id              = var.DATA_HIGHWAY_PEERING_CONNECTION_ID
}

resource "aws_route" "data-highway-private-1a-to-automation-private-1a" {
  route_table_id = aws_route_table.automation-private-1a.id
  destination_cidr_block = var.AUTOMATION_CIDR_PRIVATE_1A[var.CURRENT_ENVIRONMENT]
  vpc_peering_connection_id = data.aws_vpc_peering_connection.data-highway-peering-connection.id
}

resource "aws_route" "data-highway-private-1a-to-automation-private-1b" {
  route_table_id = aws_route_table.automation-private-1a.id
  destination_cidr_block = var.AUTOMATION_CIDR_PRIVATE_1B[var.CURRENT_ENVIRONMENT]
  vpc_peering_connection_id = data.aws_vpc_peering_connection.data-highway-peering-connection.id
}

resource "aws_route" "data-highway-private-1b-to-automation-private-1a" {
  route_table_id = aws_route_table.automation-private-1b.id
  destination_cidr_block = var.AUTOMATION_CIDR_PRIVATE_1A[var.CURRENT_ENVIRONMENT]
  vpc_peering_connection_id = data.aws_vpc_peering_connection.data-highway-peering-connection.id
}

resource "aws_route" "data-highway-private-1b-to-automation-private-1b" {
  route_table_id = aws_route_table.automation-private-1b.id
  destination_cidr_block = var.AUTOMATION_CIDR_PRIVATE_1B[var.CURRENT_ENVIRONMENT]
  vpc_peering_connection_id = data.aws_vpc_peering_connection.data-highway-peering-connection.id
}
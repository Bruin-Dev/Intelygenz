/*====
The VPC
======*/

resource "aws_vpc" "automation-vpc" {
  cidr_block = var.cidr_vars[var.CURRENT_ENVIRONMENT]["cidr_base"]
  enable_dns_hostnames = true
  enable_dns_support = true

  tags = {
    Name = local.automation-vpc-tag-Name
  }
}

/*====
Subnets
======*/
/* Internet gateway for the public subnet */
resource "aws_internet_gateway" "automation-igw" {
  vpc_id = aws_vpc.automation-vpc.id

  tags = {
    Name = local.automation-internet_gateway-tag-Name
  }
}


/* Elastic IP for NAT */
resource "aws_eip" "automation-nat_eip-1a" {
  vpc = true
  tags = {
    Name = local.automation-nat_eip-1a-tag-Name
  }
}

resource "aws_eip" "automation-nat_eip-1b" {
  vpc = true
  tags = {
    Name = local.automation-nat_eip-1b-tag-Name
  }
}

/* NAT */
resource "aws_nat_gateway" "automation-nat-1a" {
  allocation_id = aws_eip.automation-nat_eip-1a.id
  subnet_id = aws_subnet.automation-public_subnet-1a.id

  tags = {
    Name = local.automation-nat_gateway-1a-tag-Name
  }
}

resource "aws_nat_gateway" "automation-nat-1b" {
  allocation_id = aws_eip.automation-nat_eip-1b.id
  subnet_id = aws_subnet.automation-public_subnet-1b.id

  tags = {
    Name = local.automation-nat_gateway-1b-tag-Name
  }
}

/* Public subnet */
resource "aws_subnet" "automation-public_subnet-1a" {
  vpc_id = aws_vpc.automation-vpc.id
  cidr_block = var.cdir_public_1
  availability_zone = "us-east-1a"
  map_public_ip_on_launch = true

  tags = {
    Name = local.automation-public_subnet-1a-tag-Name
  }
}

resource "aws_subnet" "automation-public_subnet-1b" {
  vpc_id = aws_vpc.automation-vpc.id
  cidr_block = var.cdir_public_2
  availability_zone = "us-east-1b"
  map_public_ip_on_launch = true

  tags = {
    Name = local.automation-public_subnet-1b-tag-Name
  }
}

/* Private subnet */
resource "aws_subnet" "automation-private_subnet-1a" {
  vpc_id = aws_vpc.automation-vpc.id
  cidr_block = var.cdir_private_1
  availability_zone = "us-east-1a"
  map_public_ip_on_launch = false

  tags = {
    Name = local.automation-private_subnet-1a-tag-Name
  }
}

resource "aws_subnet" "automation-private_subnet-1b" {
  vpc_id = aws_vpc.automation-vpc.id
  cidr_block = var.cdir_private_2
  availability_zone = "us-east-1b"
  map_public_ip_on_launch = false

  tags ={
    Name = local.automation-private_subnet-1b-tag-Name
  }
}

/* Routing table for private subnets */
resource "aws_route_table" "automation-private-1a" {
  vpc_id = aws_vpc.automation-vpc.id

  tags = {
    Name = local.automation-private-route_table-1a-tag-Name
  }
}

resource "aws_route_table" "automation-private-1b" {
  vpc_id = aws_vpc.automation-vpc.id

  tags = {
    Name = local.automation-private-route_table-1b-tag-Name
  }
}

/* Routing table for public subnet */
resource "aws_route_table" "automation-public" {
  vpc_id = aws_vpc.automation-vpc.id

  tags = {
    Name = local.automation-public-route_table-tag-Name
  }
}

resource "aws_route" "automation-igw-public" {
  route_table_id = aws_route_table.automation-public.id
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
  route_table_id = aws_route_table.automation-public.id
}

resource "aws_route_table_association" "automation-public-1b" {
  subnet_id = aws_subnet.automation-public_subnet-1b.id
  route_table_id = aws_route_table.automation-public.id
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
    Name = local.automation-default-security_group-tag-Name
  }
}

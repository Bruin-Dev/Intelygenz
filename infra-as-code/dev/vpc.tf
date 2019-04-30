/*====
The VPC
======*/

resource "aws_vpc" "automation-vpc" {
  cidr_block = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support = true

  tags {
    Name = "${var.environment}"
    Environment = "${var.environment}"
  }
}

/*====
Subnets
======*/
/* Internet gateway for the public subnet */
resource "aws_internet_gateway" "automation-igw" {
  vpc_id = "${aws_vpc.automation-vpc.id}"

  tags {
    Name = "${var.environment}"
    Environment = "${var.environment}"
  }
}


/* Elastic IP for NAT */
resource "aws_eip" "automation-nat_eip-1a" {
  vpc = true
  tags {
    Name = "${var.environment}-nat-1a"
  }
}
resource "aws_eip" "automation-nat_eip-1b" {
  vpc = true
  tags {
    Name = "${var.environment}-nat-1b"
  }
}

/* NAT */
resource "aws_nat_gateway" "automation-nat-1a" {
  allocation_id = "${aws_eip.automation-nat_eip-1a.id}"
  subnet_id = "${aws_subnet.automation-public_subnet-1a.id}"

  tags {
    Name = "${var.environment}-1a"
    Environment = "${var.environment}"
  }
}
resource "aws_nat_gateway" "automation-nat-1b" {
  allocation_id = "${aws_eip.automation-nat_eip-1b.id}"
  subnet_id = "${aws_subnet.automation-public_subnet-1b.id}"

  tags {
    Name = "${var.environment}-1b"
    Environment = "${var.environment}"
  }
}

/* Public subnet */
resource "aws_subnet" "automation-public_subnet-1a" {
  vpc_id = "${aws_vpc.automation-vpc.id}"
  cidr_block = "10.0.1.0/24"
  availability_zone = "us-east-1a"
  map_public_ip_on_launch = true

  tags {
    Name = "${var.environment}-public-subnet-1a"
    Environment = "${var.environment}"
  }
}
resource "aws_subnet" "automation-public_subnet-1b" {
  vpc_id = "${aws_vpc.automation-vpc.id}"
  cidr_block = "10.0.2.0/24"
  availability_zone = "us-east-1b"
  map_public_ip_on_launch = true

  tags {
    Name = "${var.environment}-public-subnet-1b"
    Environment = "${var.environment}"
  }
}

/* Private subnet */
resource "aws_subnet" "automation-private_subnet-1a" {
  vpc_id = "${aws_vpc.automation-vpc.id}"
  cidr_block = "10.0.10.0/24"
  availability_zone = "us-east-1a"
  map_public_ip_on_launch = false

  tags {
    Name = "${var.environment}-private-subnet-1a"
    Environment = "${var.environment}"
  }
}

resource "aws_subnet" "automation-private_subnet-1b" {
  vpc_id = "${aws_vpc.automation-vpc.id}"
  cidr_block = "10.0.11.0/24"
  availability_zone = "us-east-1b"
  map_public_ip_on_launch = false

  tags {
    Name = "${var.environment}-private-subnet-1b"
    Environment = "${var.environment}"
  }
}

/* Routing table for private subnet */
resource "aws_route_table" "automation-private" {
  vpc_id = "${aws_vpc.automation-vpc.id}"

  tags {
    Name = "${var.environment}-private-route-table"
    Environment = "${var.environment}"
  }
}

/* Routing table for public subnet */
resource "aws_route_table" "automation-public" {
  vpc_id = "${aws_vpc.automation-vpc.id}"

  tags {
    Name = "${var.environment}-public-route-table"
    Environment = "${var.environment}"
  }
}

resource "aws_route" "automation-igw-public" {
  route_table_id = "${aws_route_table.automation-public.id}"
  destination_cidr_block = "0.0.0.0/0"
  gateway_id = "${aws_internet_gateway.automation-igw.id}"
}

resource "aws_route" "automation-nat-private" {
  route_table_id = "${aws_route_table.automation-private.id}"
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id = "${aws_nat_gateway.automation-nat-1a.id}"
}

/* Route table associations */
resource "aws_route_table_association" "automation-public-1a" {
  subnet_id = "${aws_subnet.automation-public_subnet-1a.id}"
  route_table_id = "${aws_route_table.automation-public.id}"
}
resource "aws_route_table_association" "automation-public-1b" {
  subnet_id = "${aws_subnet.automation-public_subnet-1b.id}"
  route_table_id = "${aws_route_table.automation-public.id}"
}

resource "aws_route_table_association" "automation-private-1a" {
  subnet_id = "${aws_subnet.automation-private_subnet-1a.id}"
  route_table_id = "${aws_route_table.automation-private.id}"
}
resource "aws_route_table_association" "automation-private-1b" {
  subnet_id = "${aws_subnet.automation-private_subnet-1b.id}"
  route_table_id = "${aws_route_table.automation-private.id}"
}

/*====
VPC's Default Security Group
======*/
resource "aws_security_group" "automation-default" {
  name = "${var.environment}-default-sg"
  description = "Default security group to allow inbound/outbound from the VPC"
  vpc_id = "${aws_vpc.automation-vpc.id}"

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

  tags {
    Name = "${var.environment}-default"
  }
}
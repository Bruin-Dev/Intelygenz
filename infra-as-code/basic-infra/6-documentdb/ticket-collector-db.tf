### DocumentDB database for ticket-collector

resource "aws_db_subnet_group" "db_subnet_group" {
  count      = var.CURRENT_ENVIRONMENT == "production" ? 1 : 0
  name       = "${local.docdb-ticket-collector-cluster}-subnet-group"
  subnet_ids = data.aws_subnet_ids.mettel-automation-private-subnets.ids

  tags = {
    Name = "${local.docdb-ticket-collector-cluster}-subnet-group"
    Environment = var.CURRENT_ENVIRONMENT
    Project = local.project_name
  }
}

resource "aws_security_group" "docdb_security_group" {
  count    = var.CURRENT_ENVIRONMENT == "production" ? 1 : 0
  name     = "${local.docdb-ticket-collector-cluster}-security-group"
  vpc_id   = data.aws_vpc.mettel-automation-vpc.id

  ingress {
    description = "Allow connections from ticket-collector"
    from_port   = 27017
    to_port     = 27017
    protocol    = "tcp"
    cidr_blocks = [var.cdir_private_1[production],var.cdir_private_2[production]]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_docdb_cluster_parameter_group" "docdb_parameter_group" {
  count  = var.CURRENT_ENVIRONMENT == "production" ? 1 : 0
  family = "docdb4.0"
  name   = "${local.docdb-ticket-collector-cluster}-parameter-group"

  parameter {
    name  = "tls"
    value = "enabled"
  }

  tags = {
    Name = "${local.docdb-ticket-collector-cluster}-parameter-group"
    Environment = var.CURRENT_ENVIRONMENT
    Project = local.project_name
  }
}

resource "random_password" "documentdb-password" {
  count   = var.CURRENT_ENVIRONMENT == "production" ? 1 : 0
  length  = 16
  special = false
}

resource "aws_docdb_cluster" "docdb" {
  count                   = var.CURRENT_ENVIRONMENT == "production" ? 1 : 0
  cluster_identifier      = "${local.docdb-ticket-collector-cluster}-docdb-cluster"
  engine                  = "docdb"
  master_username         = var.TICKET_COLLECTOR_DOCUMENTDB_USERNAME
  master_password         = random_password.documentdb-password[0].result
  backup_retention_period = 5
  preferred_backup_window = "07:00-09:00"
  skip_final_snapshot     = true
  db_subnet_group_name    = aws_db_subnet_group.db_subnet_group[0].id
  vpc_security_group_ids  = [aws_security_group.docdb_security_group[0].id]
  db_cluster_parameter_group_name = aws_docdb_cluster_parameter_group.docdb_parameter_group[0].name

  tags = {
    Name = "${local.docdb-ticket-collector-cluster}-docdb-cluster"
    Environment = var.CURRENT_ENVIRONMENT
    Project = local.project_name
  }
}

resource "aws_docdb_cluster_instance" "data_collector_docdb_instance_1" {
  count              = var.CURRENT_ENVIRONMENT == "production" ? 1 : 0
  identifier         = "${local.docdb-ticket-collector-cluster}-docdb-instance-1"
  cluster_identifier = aws_docdb_cluster.docdb[0].id
  instance_class     = "db.t3.medium"

  tags = {
    Name = "${local.docdb-ticket-collector-cluster}-docdb-instance-1"
    Environment = var.CURRENT_ENVIRONMENT
    Project = local.project_name
  }
}

resource "aws_docdb_cluster_instance" "data_collector_docdb_instance_2" {
  count              = var.CURRENT_ENVIRONMENT == "production" ? 1 : 0
  identifier         = "${local.docdb-ticket-collector-cluster}-docdb-instance-2"
  cluster_identifier = aws_docdb_cluster.docdb[0].id
  instance_class     = "db.t3.medium"

  tags = {
    Name = "${local.docdb-ticket-collector-cluster}-docdb-instance-2"
    Environment = var.CURRENT_ENVIRONMENT
    Project = local.project_name
  }
}

resource "aws_security_group" "data_collector_docdb_sg" {
  count = local.count-resources-rest-api-data-collector
  
  name        = local.docdb-data-collector-security_group-name
  vpc_id      = data.terraform_remote_state.tfstate-network-resources.outputs.vpc_automation_id

  ingress {
    description = "Allow connections from data-collector lambda"
    from_port   = 27017
    to_port     = 27017
    protocol    = "tcp"
    security_groups = [aws_security_group.data_collector_lambda_sg[0].id]
  }

  egress {
    from_port       = 0
    to_port         = 0
    protocol        = "-1"
    cidr_blocks     = ["0.0.0.0/0"]
  }
}

resource "aws_docdb_subnet_group" "docdb_subnet_data_collector" {
  count = local.count-resources-rest-api-data-collector

  name       = local.docdb-data-collector-subnet_group-name

  subnet_ids = [
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1a.id,
      data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-private-1b.id
  ]

  tags = {
    Name = local.docdb-data-collector-subnet_group-name
    Environment = var.CURRENT_ENVIRONMENT
    Project = local.project_name
  }
}

resource "aws_docdb_cluster_instance" "data_collector_docdb_instance" {
  count = local.count-resources-rest-api-data-collector

  identifier         = local.docdb-data-collector-cluster_instance-name

  cluster_identifier = aws_docdb_cluster.data_collector_docdb_cluster[0].id

  instance_class     = var.docdb_instance_class_data-collector

  tags = {
    Name = local.docdb-data-collector-cluster_instance-name
    Environment = var.CURRENT_ENVIRONMENT
    Project = local.project_name
  }
}

resource "aws_docdb_cluster_parameter_group" "data_collector_docdb_pg" {
  count = local.count-resources-rest-api-data-collector

  family = "docdb3.6"
  name = local.docdb-data-collector-parameter_group

  parameter {
    name  = "tls"
    value = "enabled"
  }

  tags = {
    Name = local.docdb-data-collector-parameter_group
    Environment = var.CURRENT_ENVIRONMENT
    Project = local.project_name
  }
}

resource "aws_docdb_cluster" "data_collector_docdb_cluster" {
  count = local.count-resources-rest-api-data-collector

  skip_final_snapshot     = true
  db_subnet_group_name    = aws_docdb_subnet_group.docdb_subnet_data_collector[0].name
  cluster_identifier      = local.docdb-data-collector-cluster-identifier
  engine                  = "docdb"
  master_username         = var.DOCDB_CLUSTER_MASTER_USERNAME
  master_password         = var.DOCDB_CLUSTER_MASTER_PASSWORD
  db_cluster_parameter_group_name = aws_docdb_cluster_parameter_group.data_collector_docdb_pg[0].name
  vpc_security_group_ids = [aws_security_group.data_collector_docdb_sg[0].id]

  tags = {
    Name = local.docdb-data-collector-cluster-identifier
    Environment = var.CURRENT_ENVIRONMENT
    Project = local.project_name
  }
}
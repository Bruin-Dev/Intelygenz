resource "aws_docdb_cluster" "docdb" {
  cluster_identifier      = "ticket-collector"
  engine                  = "docdb"
  master_username         = var.documentdb-username
  master_password         = random_password.documentdb-password.result
  backup_retention_period = 5
  preferred_backup_window = "07:00-09:00"
  skip_final_snapshot     = true
  db_subnet_group_name    =
  vpc_security_group_ids  =
}

resource "random_password" "documentdb-password" {
  length = 16
  special = false
}

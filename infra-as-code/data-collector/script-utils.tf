resource "null_resource" "add_docdb_pem_to_zip_data_collector_lambda" {
  count = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 0

  provisioner "local-exec" {
    command = "wget https://s3.amazonaws.com/rds-downloads/rds-combined-ca-bundle.pem && zip -g ${path.module}/lambdas/rest-api-data-collector/rest-api-data-collector.zip rds-combined-ca-bundle.pem"
  }

  triggers = {
    always_run = timestamp()
  }

}
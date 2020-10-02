locals {
  // Project common attributes
  project_name = "mettel-automation"

  // api-gateway local vars
  api-gateway-data-collector = "data-collector-api-gateway-${var.CURRENT_ENVIRONMENT}"

  // data-collector lambda local vars
  rest-api-data-collector-lambda-security_group-name = "data-collector-${var.CURRENT_ENVIRONMENT}"
  rest-api-data-collector-lambda-function_name = "data-collector-${var.CURRENT_ENVIRONMENT}"

  // DocumentDB data-collector local vars
  docdb-data-collector-security_group-name = "docdb-data-collector-${var.CURRENT_ENVIRONMENT}"
  docdb-data-collector-subnet_group-name = "docdb-data-collector-${var.CURRENT_ENVIRONMENT}"
  docdb-data-collector-cluster_instance-name = "data-collector-${var.CURRENT_ENVIRONMENT}"
  docdb-data-collector-parameter_group = "data-collector-${var.CURRENT_ENVIRONMENT}"
  docdb-data-collector-cluster-identifier = "data-collector-docdb-${var.CURRENT_ENVIRONMENT}"
}
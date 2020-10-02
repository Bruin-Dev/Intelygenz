variable "CURRENT_ENVIRONMENT" {
  default = "dev"
  description = "Name of the environment to identify the network resources to be used"
  type = "string"
}

// data-collector DocumentDB variables
variable "docdb_instance_class_data-collector" {
  default = "db.t3.medium"
  description = "Instance class used for DocumentDB used by data-collector lambda"
}

variable "DOCDB_CLUSTER_MASTER_USERNAME" {
  default = "mast"
  description = "Username for the master DB user"
}

variable "DOCDB_CLUSTER_MASTER_PASSWORD" {
  default = "test"
  description = "Password for the master DB user"
}

variable "REST_API_DATA_COLLECTOR_MONGODB_COLLECTION" {
  default = "data"
  description = "MongoDB's collection used by the lambda data-collector"
}

variable "REST_API_DATA_COLLECTOR_MONGODB_DATABASE" {
  default = "db"
  description = "MongoDB's database used by the lambda data-collector"
}

variable "REST_API_DATA_COLLECTOR_AUTH_TOKEN" {
  default = ""
  description = "Auth token used in data-collector lambda function"
}

variable "REST_API_DATA_COLLECTOR_MONGODB_QUERYSTRING" {
  default = "ssl=true&ssl_ca_certs=rds-combined-ca-bundle.pem&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false"
  description = "MongoDB's querystring"
}
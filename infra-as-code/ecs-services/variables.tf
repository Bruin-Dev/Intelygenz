variable "ENVIRONMENT" {
}

variable "domain" {
  default = "mettel-automation.net"
}

variable "SUBDOMAIN" {
}

variable "BUILD_NUMBER" {
  default = ""
}

variable "LAST_CONTACT_RECIPIENT" {
  default = ""
}

variable "PYTHONUNBUFFERED" {
  default = 1
}

variable "EMAIL_ACC_PWD" {
  default = ""
}

variable "NATS_CLUSTER_NAME" {
  default = "automation-engine-nats"
}

variable "MONITORING_SECONDS" {
  default = "600"
}

variable "VELOCLOUD_CREDENTIALS" {
  default = ""
}

variable "VELOCLOUD_VERIFY_SSL" {
  default = "yes"
}

variable "BRUIN_CLIENT_ID" {
  default = ""
}

variable "BRUIN_CLIENT_SECRET" {
  default = ""
}

variable "BRUIN_LOGIN_URL" {
  default = ""
}

variable "BRUIN_BASE_URL" {
  default = ""
}

variable "T7_BASE_URL"{
  default = ""
}

variable "T7_TOKEN"{
  default = ""
}
variable "cdir_base" {
  default = "10.1.0.0"
}

variable "CURRENT_ENVIRONMENT" {
  default = "dev"
}

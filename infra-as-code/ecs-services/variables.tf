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

variable "cidr_base" {
  type = "map"
  default = {
    "production"  = "10.1.0.0/16"
    "dev"         = "10.2.0.0/16"
  }
}

variable "CURRENT_ENVIRONMENT" {
  default = "dev"
  description = "Name of the environment to identify the network resources to be used"
  type = "string"
}

variable "ALARMS_SUBSCRIPTIONS_EMAIL_ADDRESS" {
  type = "string"
  description = "Email addresses to send notifications generated by alarm of errors and exceptions detected in services"
  default = "xoan.mallon@intelygenz.com"
}

variable "env_network_resources" {
  type = "string"
  description = "Variable for references to common network resources per environment"
  default = "xoan.mallon@intelygenz.com,sancho.munoz@intelygenz.com"
}

variable "alarms_protocol" {
  default     = "email"
  description = "SNS Protocol to use. email or email-json"
  type        = "string"
}
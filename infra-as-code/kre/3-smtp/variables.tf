# IGZ user for create email accounts
variable "igz_users_email" {
  type = list
  default = [
//    "brandon.samudio@intelygenz.com",
//    "daniel.fernandez@intelygenz.com",
//    "joseluis.vega@intelygenz.com",
//    "juancarlos.gomez@intelygenz.com",
//    "julia.hossu@intelygenz.com",
//    "sancho.munoz@intelygenz.com",
    "jonas.dacruz@intelygenz.com",
    "angel.sanchez@intelygenz.com",
    "gustavo.marin@intelygenz.com",
    "mettel@intelygenz.com",
    "francisco.capllonch@intelygenz.com",
    "xoan.mallon@intelygenz.com"
  ]
}

variable "subdomain_name_prefix" {
  type = string
  default = "intelygenz"
}

variable "region" {
  type = string
  default = "us-east-1"
}

variable "enable_spf_record" {
  type = bool
  default = true
}

variable "extra_ses_records" {
  type    = list(string)
  default = []
}
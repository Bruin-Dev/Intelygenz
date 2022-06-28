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
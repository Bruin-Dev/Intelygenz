# -----------------------------------------------------------
# REQUIRED PARAMETERS
# You must provide a value for each of these parameters.
# -----------------------------------------------------------

variable "prefix" {
  description = "the name of the project"
}

variable "environment" {
  description = "the environment"
}

variable "region" {
  description = "region to deploy databases"
}

variable "logs_buckets" {
  description = "bucket for put logs"
}

variable "ssl_certificate" {
  description = "certificate to use in cloudfront"
}

variable "index_document" {
  description = "index document"
}

variable "error_document" {
  description = "error document"
}

variable "referer_header" {
  description = "Referer header (random text) to set to cloudfront in all request, this is used to allow give access to the bucket"
}

variable "vpn_remote_ipset" {
  description = "list of ips to allow access"
  type        = list(map(string))
  default     = []
}

variable "domain_name" {
  description = "domain name to use in cloudfront"
  type        = list(string)
}
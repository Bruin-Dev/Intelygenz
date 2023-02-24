variable "common_info" {
  type = map(string)
}

variable "service_affecting_monitor_s3_bucket_name" {
  description = "Service Affection monitor s3 bucket name to put files in that bucket."
  sensitive   = true
  type        = string
}

variable "service_affecting_monitor_s3_access_key" {
  description = "Service Affection monitor s3 service account access key."
  sensitive   = true
  type        = string
}

variable "service_affecting_monitor_s3_secret_key" {
  description = "Service Affection monitor s3 service account secret key."
  sensitive   = true
  type        = string
}

variable "global_ssm_kms_name" {
  description = "Global KMS key name to encrypt SSM parameters."
  sensitive   = true
  type        = string
}

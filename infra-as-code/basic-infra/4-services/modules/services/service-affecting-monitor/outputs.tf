
output "ssm_parameter_name_service_affecting_s3_service_account_access_key" {
  description = aws_ssm_parameter.service-affecting-s3-service-account-access-key.description
  value       = aws_ssm_parameter.service-affecting-s3-service-account-access-key.name
  sensitive   = true
}

output "ssm_parameter_name_service_affecting_s3_service_account_secret_key" {
  description = aws_ssm_parameter.service-affecting-s3-service-account-secret-key.description
  value       = aws_ssm_parameter.service-affecting-s3-service-account-secret-key.name
  sensitive   = true
}

output "ssm_parameter_name_service_affecting_s3_bucket_name" {
  description = aws_ssm_parameter.service-affecting-s3-bucket-name.description
  value       = aws_ssm_parameter.service-affecting-s3-bucket-name.name
  sensitive   = true
}

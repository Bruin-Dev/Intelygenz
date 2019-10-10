output "vpc_automation_id" {
  value = aws_vpc.automation-vpc.id
}

output "subnet_automation-private-1a" {
  value = aws_subnet.automation-private_subnet-1a[var.CURRENT_ENVIRONMENT]
}

output "subnet_automation-private-1b" {
  value = aws_subnet.automation-private_subnet-1b[var.CURRENT_ENVIRONMENT]
}

output "subnet_automation-public-1a" {
  value = aws_subnet.automation-public_subnet-1a[var.CURRENT_ENVIRONMENT]
}

output "subnet_automation-public-1b" {
  value = aws_subnet.automation-public_subnet-1b[var.CURRENT_ENVIRONMENT]
}
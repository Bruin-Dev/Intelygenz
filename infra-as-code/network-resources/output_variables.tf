output "vpc_automation_id" {
  description = "VPC identifier for the environment"
  value       = aws_vpc.automation-vpc.id
}

output "subnet_automation-private-1a" {
  description = "Information details about private subnet 1a"
  value       = aws_subnet.automation-private_subnet-1a
}

output "subnet_automation-private-1b" {
  description = "Information details about private subnet 1b"
  value       = aws_subnet.automation-private_subnet-1b
}

output "subnet_automation-public-1a" {
  description = "Information details about public subnet 1a"
  value       = aws_subnet.automation-public_subnet-1a
}

output "subnet_automation-public-1b" {
  description = "Information details about public subnet 1b"
  value       = aws_subnet.automation-public_subnet-1b
}
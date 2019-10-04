output "vpc_automation_id" {
  value = aws_vpc.automation-vpc.id
}

output "subnet_automation-private-1a" {
  value = aws_subnet.automation-private_subnet-1a.id
}

output "subnet_automation-private-1b" {
  value = aws_subnet.automation-private_subnet-1b.id
}
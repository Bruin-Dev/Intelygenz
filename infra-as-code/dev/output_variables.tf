output "ecs_execution_role" {
  value = "${data.aws_iam_role.ecs_execution_role.arn}"
}

output "automation_cluster_id" {
  value = "${aws_ecs_cluster.automation.id}"
}

output "vpc_automation_id" {
  value = "${aws_vpc.automation-vpc.id}"
}

output "aws_service_discovery_automation-zone_id" {
  value = "${aws_service_discovery_private_dns_namespace.automation-zone.id}"
}

output "subnet_automation-private-1a" {
  value = "${aws_subnet.automation-private_subnet-1a.id}"
}

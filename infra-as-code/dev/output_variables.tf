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

output "subnet_automation-private-1b" {
  value = "${aws_subnet.automation-private_subnet-1b.id}"
}

output "redis_hostname" {
  value = "${aws_elasticache_cluster.automation-redis.cache_nodes.0.address}"
}

output "automation_alb" {
  value = "${aws_lb.automation-alb}"
}
output "automation_alb_arn" {
  value = "${aws_lb.automation-alb.arn}"
}

output "cert_mettel" {
  value = "${data.aws_acm_certificate.automation.arn}"
}
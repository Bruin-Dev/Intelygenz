data "aws_ecr_repository" "automation-velocloud-orchestrator" {
  name = "${var.environment}-velocloud-orchestrator"
}

data "template_file" "automation-velocloud-orchestrator" {
  template = "${file("${path.module}/task-definitions/velocloud_orchestrator.json")}"

  vars = {
    image = "${data.aws_ecr_repository.automation-velocloud-orchestrator.repository_url}:${var.BUILD_NUMBER}"
    log_group = "${var.environment}"
    log_prefix = "${var.environment}-${var.BUILD_NUMBER}"

    PYTHONUNBUFFERED = "${var.PYTHONUNBUFFERED}"
    NATS_SERVER1 = "nats://nats-server.${var.environment}.local:4222"
    NATS_CLUSTER_NAME = "${var.NATS_CLUSTER_NAME}"
    MONITORING_SECONDS = "${var.MONITORING_SECONDS}"
    LOST_CONTACT_RECIPIENT = "${var.LOST_CONTACT_RECIPIENT}"
    REDIS_HOSTNAME = "${aws_elasticache_cluster.automation-redis.cache_nodes.0.address}"
  }
}

resource "aws_ecs_task_definition" "automation-velocloud-orchestrator" {
  family = "${var.environment}-velocloud-orchestrator"
  container_definitions = "${data.template_file.automation-velocloud-orchestrator.rendered}"
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "256"
  memory = "512"
  execution_role_arn = "${aws_iam_role.ecs_execution_role.arn}"
  task_role_arn = "${aws_iam_role.ecs_execution_role.arn}"
}

resource "aws_security_group" "automation-velocloud-orchestrator_service" {
  vpc_id = "${aws_vpc.automation-vpc.id}"
  name = "${var.environment}-velocloud-orchestrator"
  description = "Allow egress from container"

  lifecycle {
    create_before_destroy = true
  }

  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = [
      "0.0.0.0/0"]
  }

  ingress {
    from_port = 8
    to_port = 0
    protocol = "icmp"
    cidr_blocks = [
      "0.0.0.0/0"]
  }

  ingress {
    from_port = 5000
    to_port = 5000
    protocol = "TCP"
    cidr_blocks = [
      "0.0.0.0/0"
    ]
  }

  ingress {
    from_port = 9090
    to_port = 9090
    protocol = "TCP"
    cidr_blocks = [
      "${var.cdir_base}/16"
    ]
  }

  tags = {
    Name = "${var.environment}-velocloud-orchestrator"
    Environment = "${var.environment}"
  }
}

resource "aws_service_discovery_service" "velocloud-orchestrator" {
  name = "velocloud-orchestrator"

  dns_config {
    namespace_id = "${aws_service_discovery_private_dns_namespace.automation-zone.id}"

    dns_records {
      ttl = 10
      type = "A"
    }

    routing_policy = "MULTIVALUE"
  }

  health_check_custom_config {
    failure_threshold = 1
  }
}

resource "aws_ecs_service" "automation-velocloud-orchestrator" {
  name = "${var.environment}-velocloud-orchestrator"
  task_definition = "${aws_ecs_task_definition.automation-velocloud-orchestrator.family}:${aws_ecs_task_definition.automation-velocloud-orchestrator.revision}"
  desired_count = 1
  launch_type = "FARGATE"
  cluster = "${aws_ecs_cluster.automation.id}"

  network_configuration {
    security_groups = [
      "${aws_security_group.automation-velocloud-orchestrator_service.id}"]
    subnets = [
      "${aws_subnet.automation-private_subnet-1a.id}",
      "${aws_subnet.automation-private_subnet-1b.id}"]
    assign_public_ip = false
  }

  service_registries {
    registry_arn = "${aws_service_discovery_service.velocloud-orchestrator.arn}"
  }
}

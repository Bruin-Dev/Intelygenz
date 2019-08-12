data "aws_ecr_repository" "automation-bruin-bridge" {
  name = "automation-bruin-bridge"
}

data "template_file" "automation-bruin-bridge" {
  template = "${file("${path.module}/task-definitions/bruin_bridge.json")}"

  vars = {
    image = "${data.aws_ecr_repository.automation-bruin-bridge.repository_url}:${var.BUILD_NUMBER}"
    log_group = "${var.ENVIRONMENT}"
    log_prefix = "${var.ENVIRONMENT}-${var.BUILD_NUMBER}"

    PYTHONUNBUFFERED = "${var.PYTHONUNBUFFERED}"
    NATS_SERVER1 = "nats://nats-server.${var.ENVIRONMENT}.local:4222"
    NATS_CLUSTER_NAME = "${var.NATS_CLUSTER_NAME}"
    BRUIN_CLIENT_ID = "${var.BRUIN_CLIENT_ID}"
    BRUIN_CLIENT_SECRET = "${var.BRUIN_CLIENT_SECRET}"
    BRUIN_LOGIN_URL = "${var.BRUIN_LOGIN_URL}"
    BRUIN_BASE_URL = "${var.BRUIN_BASE_URL}"
  }
}

resource "aws_ecs_task_definition" "automation-bruin-bridge" {
  family = "${var.ENVIRONMENT}-bruin-bridge"
  container_definitions = "${data.template_file.automation-bruin-bridge.rendered}"
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "256"
  memory = "512"
  execution_role_arn = "${data.terraform_remote_state.tfstate-dev-resources.ecs_execution_role}"
  task_role_arn = "${data.terraform_remote_state.tfstate-dev-resources.ecs_execution_role}"
}

resource "aws_security_group" "automation-bruin-bridge_service" {
  vpc_id = "${aws_vpc.automation-vpc.id}"
  name = "${var.ENVIRONMENT}-bruin-bridge"
  description = "Allow egress from container"

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
    Name = "${var.ENVIRONMENT}-bruin-bridge"
    Environment = "${var.ENVIRONMENT}"
  }
}
resource "aws_service_discovery_service" "bruin-bridge" {
  name = "bruin-bridge"

  dns_config {
    namespace_id = "${data.terraform_remote_state.tfstate-dev-resources.aws_service_discovery_automation-zone_id}"

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

resource "aws_ecs_service" "automation-bruin-bridge" {
  name = "${var.ENVIRONMENT}-bruin-bridge"
  task_definition = "${aws_ecs_task_definition.automation-bruin-bridge.family}:${aws_ecs_task_definition.automation-bruin-bridge.revision}"
  desired_count = 1
  launch_type = "FARGATE"
  cluster = "${data.terraform_remote_state.tfstate-dev-resources.automation_cluster_id}"

  network_configuration {
    security_groups = [
      "${aws_security_group.automation-bruin-bridge_service.id}"]
    subnets = [
      "${data.terraform_remote_state.tfstate-dev-resources.subnet_automation-private-1a}"]
    assign_public_ip = false
  }

  service_registries {
    registry_arn = "${aws_service_discovery_service.bruin-bridge.arn}"
  }
}

data "aws_ecr_repository" "automation-nats-server" {
  name = "automation-nats-server"
}

data "external" "nats-server-build_number" {
  program = [
    "bash",
    "${path.module}/scripts/obtain_latest_image_for_repository.sh",
    data.aws_ecr_repository.automation-nats-server.name
  ]
}

data "template_file" "automation-nats-server" {
  template = file("${path.module}/task-definitions/nats_server_seed.json")

  vars = {
    image = local.automation-nats-server-image
    log_group = var.ENVIRONMENT
    log_prefix = local.log_prefix

    CONTAINER_NAME = local.automation-nats-server-task_definition_template-container_name
    NATSCLUSTER =  local.automation-nats-server-task_definition_template-natscluster
    NATSCLUSTERPORT = var.NATS_SERVER_SEED_CLUSTER_PORT
    PORT = var.NATS_SERVER_SEED_CLIENTS_PORT
    CLUSTER_MODE = var.NATS_SERVER_SEED_CLUSTER_MODE
  }
}

resource "aws_ecs_task_definition" "automation-nats-server" {
  family = local.automation-nats-server-ecs_task_definition-family
  container_definitions = data.template_file.automation-nats-server.rendered
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "256"
  memory = "1024"
  execution_role_arn = data.aws_iam_role.ecs_execution_role.arn
  task_role_arn = data.aws_iam_role.ecs_execution_role.arn
}

resource "aws_security_group" "automation-nats_service" {
  vpc_id = data.aws_vpc.mettel-automation-vpc.id
  name = local.automation-nats-server-nats_service-security_group-name
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
    from_port = 8222
    to_port = 8222
    protocol = "TCP"
    cidr_blocks = [
      "0.0.0.0/0"
    ]
  }

  ingress {
    from_port = 4222
    to_port = 4222
    protocol = "TCP"
    cidr_blocks = [
      var.cidr_base[var.CURRENT_ENVIRONMENT]
    ]
  }

  ingress {
    from_port = var.NATS_SERVER_SEED_CLUSTER_PORT
    to_port = var.NATS_SERVER_SEED_CLUSTER_PORT
    protocol = "TCP"
    cidr_blocks = [
      var.cidr_base[var.CURRENT_ENVIRONMENT]
    ]
  }

  tags = {
    Name = local.automation-nats-server-nats_service-security_group-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_service_discovery_service" "nats-server" {
  name = "nats-server-${var.ENVIRONMENT}"

  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.automation-zone.id

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

resource "aws_ecs_service" "automation-nats-server" {
  name = local.automation-nats-server-ecs_service-name
  task_definition = local.automation-nats-server-ecs_service-task_definition
  desired_count = var.nats_server_desired_tasks
  launch_type = "FARGATE"
  cluster = aws_ecs_cluster.automation.id
  count = var.nats_server_desired_tasks > 0 ? 1 : 0

  network_configuration {
    security_groups = [
      aws_security_group.automation-nats_service.id]
    subnets = data.aws_subnet_ids.mettel-automation-private-subnets.ids
    assign_public_ip = false
  }

  service_registries {
    registry_arn = aws_service_discovery_service.nats-server.arn
  }


}

data "template_file" "automation-nats-server-task-definition-output" {
  template = file("${path.module}/task-definitions/task_definition_output_template.json")

  vars = {
    task_definition_arn = aws_ecs_task_definition.automation-nats-server.arn
  }
}

resource "null_resource" "generate_nats_server_task_definition_output_json" {
  provisioner "local-exec" {
    command = format("cat <<\"EOF\" > \"%s\"\n%s\nEOF", var.nats-server-task-definition-json, data.template_file.automation-nats-server-task-definition-output.rendered)
  }
  triggers = {
    always_run = timestamp()
  }
  depends_on = [aws_ecs_task_definition.automation-nats-server]
}

resource "null_resource" "nats-server-healthcheck" {

  depends_on = [aws_ecs_service.automation-nats-server,
                aws_ecs_task_definition.automation-nats-server,
                null_resource.generate_nats_server_task_definition_output_json]

  provisioner "local-exec" {
    command = "python3 ci-utils/ecs/task_healthcheck.py -t nats-server ${var.nats-server-task-definition-json}"
  }

  triggers = {
    always_run = timestamp()
  }
}

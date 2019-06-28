resource "aws_ecr_repository" "automation-velocloud-bridge" {
  name = "${var.ENVIRONMENT}-velocloud-bridge"
}

data "template_file" "automation-velocloud-bridge" {
  template = "${file("${path.module}/task-definitions/velocloud_bridge.json")}"

  vars {
    image = "${aws_ecr_repository.automation-velocloud-bridge.repository_url}:${var.build_number}"
    PYTHONUNBUFFERED = 1
    NATS_SERVER1 = "${var.NATS_SERVER1}"
    NATS_CLUSTER_NAME = "${var.NATS_CLUSTER_NAME}"
    VELOCLOUD_CREDENTIALS = "${var.VELOCLOUD_CREDENTIALS}"
    VELOCLOUD_VERIFY_SSL = "${var.VELOCLOUD_VERIFY_SSL}"
  }
}

resource "aws_ecs_task_definition" "automation-velocloud-bridge" {
  family = "${var.ENVIRONMENT}-velocloud-bridge"
  container_definitions = "${data.template_file.automation-velocloud-bridge.rendered}"
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "256"
  memory = "512"
  execution_role_arn = "${aws_iam_role.ecs_execution_role.arn}"
  task_role_arn = "${aws_iam_role.ecs_execution_role.arn}"
}

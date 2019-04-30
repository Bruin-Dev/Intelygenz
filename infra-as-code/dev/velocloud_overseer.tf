resource "aws_ecr_repository" "mettel-automation-pro-velocloud-overseer" {
  name = "${var.environment}-velocloud-overseer"
}

data "template_file" "mettel-automation-pro-velocloud-overseer" {
  template = "${file("${path.module}/task-definitions/velocloud_overseer.json")}"

  vars {
    image = "${aws_ecr_repository.mettel-automation-pro-velocloud-overseer.repository_url}:${var.build_number}"
    PYTHONUNBUFFERED = 1
    NATS_SERVER1 = "${var.NATS_SERVER1}"
    NATS_CLUSTER_NAME = "${var.NATS_CLUSTER_NAME}"
    VELOCLOUD_CREDENTIALS = "${var.VELOCLOUD_CREDENTIALS}"
    VELOCLOUD_VERIFY_SSL = "${var.VELOCLOUD_VERIFY_SSL}"
  }
}

resource "aws_ecs_task_definition" "mettel-automation-pro-velocloud-overseer" {
  family = "${var.environment}-velocloud-overseer"
  container_definitions = "${data.template_file.mettel-automation-pro-velocloud-overseer.rendered}"
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "512"
  memory = "4096"
  execution_role_arn = "${aws_iam_role.ecs_execution_role.arn}"
  task_role_arn = "${aws_iam_role.ecs_execution_role.arn}"
}

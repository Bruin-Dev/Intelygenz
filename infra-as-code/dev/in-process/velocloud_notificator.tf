resource "aws_ecr_repository" "mettel-automation-velocloud-notificator" {
  name = "${var.environment}-velocloud-notificator"
}

data "template_file" "mettel-automation-velocloud-notificator" {
  template = "${file("${path.module}/task-definitions/velocloud_notificator.json")}"

  vars {
    image = "${aws_ecr_repository.mettel-automation-velocloud-notificator.repository_url}:${var.build_number}"
    PYTHONUNBUFFERED = 1
    NATS_SERVER1 = "${var.NATS_SERVER1}"
    NATS_CLUSTER_NAME = "${var.NATS_CLUSTER_NAME}"
    SLACK_URL = "${var.SLACK_URL}"
    EMAIL_ACC_PWD = "${var.EMAIL_ACC_PWD}"
  }
}

resource "aws_ecs_task_definition" "mettel-automation-velocloud-notificator" {
  family = "${var.environment}-velocloud-notificator"
  container_definitions = "${data.template_file.mettel-automation-velocloud-notificator.rendered}"
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "256"
  memory = "512"
  execution_role_arn = "${aws_iam_role.ecs_execution_role.arn}"
  task_role_arn = "${aws_iam_role.ecs_execution_role.arn}"
}

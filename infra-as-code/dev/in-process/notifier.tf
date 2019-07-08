resource "aws_ecr_repository" "mettel-automation-notifier" {
  name = "${var.ENVIRONMENT}-notifier"
}

data "template_file" "mettel-automation-notifier" {
  template = "${file("${path.module}/task-definitions/notifier.json")}"

  vars {
    image = "${aws_ecr_repository.mettel-automation-notifier.repository_url}:${var.build_number}"
    PYTHONUNBUFFERED = 1
    NATS_SERVER1 = "${var.NATS_SERVER1}"
    NATS_CLUSTER_NAME = "${var.NATS_CLUSTER_NAME}"
    SLACK_URL = "${var.SLACK_URL}"
    EMAIL_ACC_PWD = "${var.EMAIL_ACC_PWD}"
  }
}

resource "aws_ecs_task_definition" "mettel-automation-notifier" {
  family = "${var.ENVIRONMENT}-notifier"
  container_definitions = "${data.template_file.mettel-automation-notifier.rendered}"
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "256"
  memory = "512"
  execution_role_arn = "${aws_iam_role.ecs_execution_role.arn}"
  task_role_arn = "${aws_iam_role.ecs_execution_role.arn}"
}

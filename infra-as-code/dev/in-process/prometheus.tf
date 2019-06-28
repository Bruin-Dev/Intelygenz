resource "aws_ecr_repository" "mettel-automation-pro-prometheus" {
  name = "${var.ENVIRONMENT}-prometheus"
}

data "template_file" "mettel-automation-pro-prometheus" {
  template = "${file("${path.module}/task-definitions/velocloud_bridge.json")}"

  vars {
    image = "${aws_ecr_repository.mettel-automation-pro-prometheus.repository_url}:${var.build_number}"
  }
}

resource "aws_ecs_task_definition" "mettel-automation-pro-prometheus" {
  family = "${var.ENVIRONMENT}-prometheus"
  container_definitions = "${data.template_file.mettel-automation-pro-prometheus.rendered}"
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "256"
  memory = "512"
  execution_role_arn = "${aws_iam_role.ecs_execution_role.arn}"
  task_role_arn = "${aws_iam_role.ecs_execution_role.arn}"
}

resource "aws_ecr_repository" "mettel-automation-pro-nats-streaming" {
  name = "${var.environment}-nats-streaming"
}

data "template_file" "mettel-automation-pro-nats-streaming" {
  template = "${file("${path.module}/task-definitions/velocloud_drone.json")}"

  vars {
    image = "${aws_ecr_repository.mettel-automation-pro-nats-streaming.repository_url}:${var.build_number}"
  }
}

resource "aws_ecs_task_definition" "mettel-automation-pro-nats-streaming" {
  family = "${var.environment}-nats-streaming"
  container_definitions = "${data.template_file.mettel-automation-pro-nats-streaming.rendered}"
  requires_compatibilities = [
    "FARGATE"]
  network_mode = "awsvpc"
  cpu = "256"
  memory = "1024"
  execution_role_arn = "${aws_iam_role.ecs_execution_role.arn}"
  task_role_arn = "${aws_iam_role.ecs_execution_role.arn}"
}

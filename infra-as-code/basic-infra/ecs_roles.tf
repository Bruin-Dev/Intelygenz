resource "aws_iam_role" "ecs_execution_role" {
  name               = "ecs_task_execution_role"
  assume_role_policy = file("${path.module}/policies/ecs-task-execution-role.json")
}

resource "aws_iam_role_policy" "automation-ecs_execution_role_policy" {
  name   = "ecs_execution_role_policy"
  policy = file("${path.module}/policies/ecs-execution-role-policy.json")
  role   = aws_iam_role.ecs_execution_role.id
}

resource "aws_iam_role" "ecs_execution_with_s3_role" {
  name               = "ecs_task_execution_with_s3_role"
  assume_role_policy = file("${path.module}/policies/ecs-task-execution-role.json")
}

resource "aws_iam_role_policy" "automation-ecs_execution_role_with_s3_policy" {
  name   = "ecs_execution_role_with_s3_policy"
  policy = file("${path.module}/policies/ecs-execution-role-with-s3-policy.json")
  role   = aws_iam_role.ecs_execution_with_s3_role.id
}

resource "aws_iam_role" "ecs_execution_with_s3_and_alb_role" {
  name               = "ecs_task_execution_with_s3_and_alb_role"
  assume_role_policy = file("${path.module}/policies/ecs-task-execution-role.json")
}

resource "aws_iam_role_policy" "automation-ecs_execution_role_with_s3_and_alb_policy" {
  name   = "ecs_execution_role_with_s3_and_alb_policy"
  policy = file("${path.module}/policies/ecs-execution-role-with-s3-and-alb-policy.json")
  role   = aws_iam_role.ecs_execution_with_s3_and_alb_role.id
}

data "aws_iam_policy_document" "ecs_service_role" {
  statement {
    effect = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type = "Service"
      identifiers = ["ecs.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ecs_role" {
  name               = "ecs_role"
  assume_role_policy = data.aws_iam_policy_document.ecs_service_role.json
}

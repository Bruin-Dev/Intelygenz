resource "aws_ecs_cluster" "automation" {
  name = var.ENVIRONMENT
  setting {
    name = "containerInsights"
    value = "enabled"
  }
}

/* role that the Amazon ECS container agent and the Docker daemon can assume */
data "aws_iam_role" "ecs_execution_role" {
  name               = "ecs_task_execution_role"
}

data "aws_iam_role" "ecs_execution_role_with_s3" {
  name               = "ecs_task_execution_with_s3_role"
}

data "aws_iam_role" "ecs_role" {
  name               = "ecs_role"
}

data "aws_iam_policy_document" "ecs_service_policy" {
  statement {
    effect = "Allow"
    resources = ["*"]
    actions = [
      "elasticloadbalancing:Describe*",
      "elasticloadbalancing:DeregisterInstancesFromLoadBalancer",
      "elasticloadbalancing:RegisterInstancesWithLoadBalancer",
      "ec2:Describe*",
      "ec2:AuthorizeSecurityGroupIngress"
    ]
  }
}

resource "aws_iam_role_policy" "ecs_service_role_policy" {
  name   = "ecs_service_role_policy"
  policy = data.aws_iam_policy_document.ecs_service_policy.json
  role   = data.aws_iam_role.ecs_role.id
}
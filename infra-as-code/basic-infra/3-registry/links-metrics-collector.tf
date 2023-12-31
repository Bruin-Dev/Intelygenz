resource "aws_ecr_repository" "links-metrics-collector-repository" {
  name = "links-metrics-collector"
  tags = {
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
    Module       = "links-metrics-collector"
  }
}

resource "aws_ecr_repository_policy" "links-metrics-collector-fedramp-pull-policy" {
  repository = aws_ecr_repository.links-metrics-collector-repository.name

  policy = <<EOF
{
    "Version": "2008-10-17",
    "Statement": [
        {
            "Sid": "new policy",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::${var.FEDERAL_ACCOUNT_ID}:root"
            },
            "Action": [
                "ecr:BatchGetImage",
                "ecr:GetDownloadUrlForLayer"
            ]
        }
    ]
}
EOF
}

resource "aws_ecr_lifecycle_policy" "links-metrics-collector-image-lifecycle" {
  repository = aws_ecr_repository.links-metrics-collector-repository.name

  policy = <<EOF
{
    "rules": [
        {
            "rulePriority": 1,
            "description": "Expire images older than 14 days",
            "selection": {
                "tagStatus": "untagged",
                "countType": "sinceImagePushed",
                "countUnit": "days",
                "countNumber": 14
            },
            "action": {
                "type": "expire"
            }
        },
        {
            "rulePriority": 2,
            "description": "Keep last 10 images",
            "selection": {
                "tagStatus": "tagged",
                "tagPrefixList": ["v"],
                "countType": "imageCountMoreThan",
                "countNumber": 10
            },
            "action": {
                "type": "expire"
            }
        }
    ]
}
EOF
}

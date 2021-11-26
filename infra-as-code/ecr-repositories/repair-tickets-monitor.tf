resource "aws_ecr_repository" "repair-tickets-monitor-repository" {
  name = "repair-tickets-monitor"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "repair-tickets-monitor"
  }
}

resource "aws_ecr_lifecycle_policy" "repair-tickets-monitor-image-untagged-lifecycle" {
  repository = aws_ecr_repository.repair-tickets-monitor-repository.name

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
        }
    ]
}
EOF
}

resource "aws_ecr_lifecycle_policy" "repair-tickets-monitor-image-tagged-lifecycle" {
  repository = aws_ecr_repository.repair-tickets-monitor-repository.name

  policy = <<EOF
{
    "rules": [
        {
            "rulePriority": 1,
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

resource "aws_ecr_repository" "lumin-billing-report-repository" {
  name = "lumin-billing-report"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "lumin-billing-report"
  }
}

resource "aws_ecr_lifecycle_policy" "lumin-billing-report-image-untagged-lifecycle" {
  repository = aws_ecr_repository.lumin-billing-report-repository.name

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

resource "aws_ecr_lifecycle_policy" "lumin-billing-report-image-tagged-lifecycle" {
  repository = aws_ecr_repository.lumin-billing-report-repository.name

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

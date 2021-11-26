resource "aws_ecr_repository" "hawkeye-outage-monitor-repository" {
  name = "hawkeye-outage-monitor"
  tags = {
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
    Module        = "hawkeye-outage-monitor"
  }
}

resource "aws_ecr_lifecycle_policy" "hawkeye-customer-cache-image-untagged-lifecycle" {
  repository = aws_ecr_repository.hawkeye-customer-cache-repository.name

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

resource "aws_ecr_lifecycle_policy" "hawkeye-customer-cache-image-tagged-lifecycle" {
  repository = aws_ecr_repository.hawkeye-customer-cache-repository.name

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

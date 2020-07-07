resource "null_resource" "papertrail_provisioning" {

  count = var.CURRENT_ENVIRONMENT == "production" ? 1 : 0

  depends_on = [
      aws_ecs_service.automation-bruin-bridge,
      aws_ecs_service.automation-cts-bridge,
      aws_ecs_service.automation-dispatch-portal-backend,
      aws_ecs_service.automation-dispatch-portal-frontend,
      aws_ecs_service.automation-last-contact-report,
      aws_ecs_service.automation-lit-bridge,
      aws_ecs_service.automation-lumin-billing-report,
      aws_ecs_service.automation-metrics-prometheus,
      aws_ecs_service.automation-nats-server,
      aws_ecs_service.automation-nats-server-1,
      aws_ecs_service.automation-nats-server-2,
      aws_ecs_service.automation-service-affecting-monitor,
      aws_ecs_service.automation-service-outage-monitor-1,
      aws_ecs_service.automation-service-outage-monitor-2,
      aws_ecs_service.automation-service-outage-monitor-3,
      aws_ecs_service.automation-service-outage-monitor-4,
      aws_ecs_service.automation-service-outage-monitor-triage,
      aws_ecs_service.automation-sites-monitor,
      aws_ecs_service.automation-t7-bridge,
      aws_ecs_service.automation-tnba-monitor,
      aws_ecs_service.automation-velocloud-bridge,
      aws_elasticache_cluster.automation-redis
  ]

  provisioner "local-exec" {
    command = "python3 ci-utils/papertrail-provisioning/app.py"
  }

  triggers = {
    always_run = timestamp()
  }
}

resource "null_resource" "get_latest_images" {
  provisioner  "local-exec" {
    command = "python3 ci-utils/ecr/ecr_util_v2.py -g True -a True -e ${var.ENVIRONMENT} -p True"
  }

  triggers = {
    always_run = timestamp()
  }
}

resource "null_resource" "bruin-bridge-build_number-latest_image" {
  provisioner  "local-exec" {
    command = "cat /tmp/latest_images_for_ecr_repositories.json | jq -r '.[] | select(.repository==${data.aws_ecr_repository.automation-bruin-bridge.name}) | .image_tag'"
  }

  triggers = {
    always_run = timestamp()
  }

  depends_on = [null_resource.get_latest_images]
}
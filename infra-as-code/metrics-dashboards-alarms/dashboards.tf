data "template_file" "cluster_dashboard_definition" {
  template = file("${path.module}/dashboard-definitions/dashboard_cluster_definition.json")
  
  vars = {
    ENVIRONMENT = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_dashboard" "cluster_dashboard" {
  dashboard_name = local.dashboard_name
  dashboard_body = data.template_file.cluster_dashboard_definition.rendered
}
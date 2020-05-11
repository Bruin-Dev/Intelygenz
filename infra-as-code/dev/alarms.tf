data "template_file" "cloudformation_sns_stack_alarms_erros_exceptions_messages" {
  template = file("${path.module}/cloudformation-templates/mettel_notification_topic_stack.json")
  vars = {
    stack_description = local.cloudformation_sns_stack_alarms_errors_exceptions_messages-description-stack
    operatorEmail_description = local.cloudformation_sns_stack_alarms_errors_exceptions_messages-description-operator_email
  }
}

resource "aws_cloudformation_stack" "sns_topic_alarms" {
  name          = local.stack_alarms-errors_exceptions_messages_in_services-name
  template_body = data.template_file.cloudformation_sns_stack_alarms_erros_exceptions_messages.rendered
  parameters = {
    OperatorEmail = var.ALARMS_SUBSCRIPTIONS_EMAIL_ADDRESS
  }
  tags = {
    Name = local.stack_alarms-errors_exceptions_messages_in_services-name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "exception_messages_services_alarm" {
  alarm_name                = local.exception_messages_services_alarm-name
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = local.exception_messages_services_alarm-evaluation_periods
  metric_name               = local.exception_detected_metric-metric_transformation-name
  namespace                 = "LogMetrics"
  period                    = local.exception_messages_services_alarm-period
  statistic                 = "Sum"
  threshold                 = local.exception_messages_services_alarm-threshold
  insufficient_data_actions = []
  alarm_description         = "This metric monitors number of exception messages for all the services in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions             = [ aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"] ]
  tags = {
    Name = local.exception_messages_services_alarm-name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "error_messages_services_alarm" {
  alarm_name                = local.error_messages_services_alarm-name
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = local.error_messages_services_alarm-evaluation_periods
  metric_name               = local.errors_detected_metric-metric_transformation-name
  namespace                 = "LogMetrics"
  period                    = local.error_messages_services_alarm-period
  statistic                 = "Sum"
  threshold                 = local.error_messages_services_alarm-threshold
  insufficient_data_actions = []
  alarm_description         = "This metric monitors number of error messages for all the services in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions             = [ aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"] ]
  tags = {
    Name = local.error_messages_services_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_sites-monitor_alarm" {
  count = var.sites_monitor_desired_tasks != 0 ? 1 : 0
  alarm_name                = local.running_task_count_sites-monitor_alarm-name
  comparison_operator       = "LessThanOrEqualToThreshold"
  evaluation_periods        = local.running_task_count_service-alarm-evaluation_periods
  metric_name               = local.running_task_count-metric_transformation-name
  namespace                 = "ECS/ContainerInsights"
  period                    = local.running_task_count_service-alarm-period
  statistic                 = "Sum"
  threshold                 = local.running_task_count_service-alarm-threshold
  insufficient_data_actions = []
  alarm_description         = "This metric monitors the number of running tasks of sites-monitor service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions             = [ aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"] ]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-sites-monitor"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_sites-monitor_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_bruin-bridge_alarm" {
  count = var.bruin_bridge_desired_tasks != 0 ? 1 : 0
  alarm_name                = local.running_task_count_bruin-bridge_alarm-name
  comparison_operator       = "LessThanOrEqualToThreshold"
  evaluation_periods        = local.running_task_count_service-alarm-evaluation_periods
  metric_name               = local.running_task_count-metric_transformation-name
  namespace                 = "ECS/ContainerInsights"
  period                    = local.running_task_count_service-alarm-period
  statistic                 = "Sum"
  threshold                 = local.running_task_count_service-alarm-threshold
  insufficient_data_actions = []
  alarm_description         = "This metric monitors the number of running tasks of bruin-bridge service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions             = [ aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"] ]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-bruin-bridge"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_bruin-bridge_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_service-affecting-monitor_alarm" {
  count = var.service_affecting_monitor_desired_tasks != 0 ? 1 : 0
  alarm_name = local.running_task_count_service-affecting-monitor_alarm-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of service-affecting-monitor service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-service-affecting-monitor"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_service-affecting-monitor_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_t7-bridge_alarm" {
  count = var.t7_bridge_desired_tasks != 0 ? 1 : 0
  alarm_name = local.running_task_count_t7-bridge_alarm-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of t7-bridge service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-t7-bridge"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_t7-bridge_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_notifier_alarm" {
  count = var.notifier_desired_tasks != 0 ? 1 : 0
  alarm_name = local.running_task_count_notifier_alarm-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of notifier service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-notifier"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_notifier_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_metrics-prometheus_alarm" {
  count = var.metrics_prometheus_desired_tasks != 0 ? 1 : 0
  alarm_name = local.running_task_count_metrics-prometheus_alarm-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of metrics-prometheus service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-metrics-prometheus"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_metrics-prometheus_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_nats-server_alarm" {
  count = var.nats_server_desired_tasks != 0 ? 1 : 0
  alarm_name = local.running_task_count_nats-server_alarm-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of nats-server service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-nats-server"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_nats-server_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_nats-server-1_alarm" {
  count = var.nats_server_1_desired_tasks != 0 ? 1 : 0
  alarm_name = local.running_task_count_nats-server-1_alarm-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of nats-server-1 service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-nats-server-1"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_nats-server-1_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_nats-server-2_alarm" {
  count = var.nats_server_2_desired_tasks != 0 ? 1 : 0
  alarm_name = local.running_task_count_nats-server-2_alarm-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of nats-server-2 service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-nats-server-2"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_nats-server-2_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}


resource "aws_cloudwatch_metric_alarm" "running_task_count_service-outage-monitor-velo1_alarm" {
  count = var.service_outage_monitor_velo1_desired_tasks != 0 ? 1 : 0
  alarm_name = local.running_task_count_service-outage-monitor-velo1_alarm-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of service-outage-monitor service for Velocloud host# 1 in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-service-outage-monitor-velo1"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_service-outage-monitor-velo1_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_service-outage-monitor-velo2_alarm" {
  count = var.service_outage_monitor_velo2_desired_tasks != 0 ? 1 : 0
  alarm_name = local.running_task_count_service-outage-monitor-velo2_alarm-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of service-outage-monitor service for Velocloud host# 1 in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-service-outage-monitor-velo2"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_service-outage-monitor-velo2_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_service-outage-monitor-velo3_alarm" {
  count = var.service_outage_monitor_velo3_desired_tasks != 0 ? 1 : 0
  alarm_name = local.running_task_count_service-outage-monitor-velo3_alarm-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of service-outage-monitor service for Velocloud host# 1 in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-service-outage-monitor-velo3"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_service-outage-monitor-velo3_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_service-outage-monitor-velo4_alarm" {
  count = var.service_outage_monitor_velo4_desired_tasks != 0 ? 1 : 0
  alarm_name = local.running_task_count_service-outage-monitor-velo4_alarm-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of service-outage-monitor service for Velocloud host# 1 in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-service-outage-monitor-velo4"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_service-outage-monitor-velo4_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_service-outage-monitor-triage_alarm" {
  count = var.service_outage_monitor_triage_desired_tasks != 0 ? 1 : 0
  alarm_name = local.running_task_count_service-outage-monitor-triage_alarm-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of service-outage-monitor service for Velocloud host# 1 in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-service-outage-monitor-triage"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_service-outage-monitor-triage_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_last-contact-report_alarm" {
  count = var.last_contact_report_desired_tasks != 0 ? 1 : 0
  alarm_name = local.running_task_count_last-contact-report_alarm-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of last-contact-report service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-last-contact-report"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_last-contact-report_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}

resource "aws_cloudwatch_metric_alarm" "running_task_count_velocloud-bridge_alarm" {
  count = var.velocloud_bridge_desired_tasks != 0 ? 1 : 0
  alarm_name = local.running_task_count_velocloud-bridge_alarm-name
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods = local.running_task_count_service-alarm-evaluation_periods
  metric_name = local.running_task_count-metric_transformation-name
  namespace = "ECS/ContainerInsights"
  period = local.running_task_count_service-alarm-period
  statistic = "Sum"
  threshold = local.running_task_count_service-alarm-threshold
  insufficient_data_actions = []
  alarm_description = "This metric monitors the number of running tasks of velocloud-bridge service in ECS cluster ${var.ENVIRONMENT}"
  alarm_actions = [
    aws_cloudformation_stack.sns_topic_alarms.outputs["TopicARN"]]
  dimensions = {
    ServiceName = "${var.ENVIRONMENT}-velocloud-bridge"
    ClusterName = var.ENVIRONMENT
  }
  tags = {
    Name = local.running_task_count_velocloud-bridge_alarm-tag-Name
    Environment = var.ENVIRONMENT
  }
}
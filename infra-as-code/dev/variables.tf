variable "ENVIRONMENT" {
  description = "Name of current environment"
}

variable "ENVIRONMENT_NAME" {
  description = "Name of current environment without automation prefix"
}

variable "SLACK_URL" {
  description = "webhook url of slack for current environment"
}

variable "TELESTAX_URL" {
  description = "Notifier telestax url"
  default = ""
}

variable "TELESTAX_ACCOUNT_SID" {
  description = "Notifier telestax account sid"
  default = ""
}

variable "TELESTAX_AUTH_TOKEN" {
  description = "Notifier telestax auth token"
  default = ""
}

variable "TELESTAX_FROM_PHONE_NUMBER" {
  description = "Notifier telestax from phone number"
  default = ""
}

variable "domain" {
  default = "mettel-automation.net"
}

variable "SUBDOMAIN" {
}

variable LOGS_RETENTION_PERIOD {
  type = "map"
  default = {
    "production" = 90
    "dev"        = 14
  }
}

variable "BUILD_NUMBER" {
  default = "latest"
}

variable "NATS_MODULE_VERSION" {
  default = "latest"
}

variable "cidr_base" {
  type = "map"
  default = {
    "production"  = "10.1.0.0/16"
    "dev"         = "172.31.84.0/22"
  }
}

variable "CURRENT_ENVIRONMENT" {
  default = "dev"
  description = "Name of the environment to identify the network resources to be used"
  type = "string"
}

variable "PYTHONUNBUFFERED" {
  default = 1
}

variable "EMAIL_ACC_PWD" {
  default = ""
}

variable "MONITORING_SECONDS" {
  default = "600"
}

// bruin-bridge environment variables

variable "BRUIN_CLIENT_ID" {
  default = ""
}

variable "BRUIN_CLIENT_SECRET" {
  default = ""
}

variable "BRUIN_LOGIN_URL" {
  default = ""
}

variable "BRUIN_BASE_URL" {
  default = ""
}

// cts-bridge environment variables

variable "CTS_CLIENT_ID" {
  default = ""
}

variable "CTS_CLIENT_SECRET" {
  default = ""
}

variable "CTS_CLIENT_USERNAME" {
  default = ""
}

variable "CTS_CLIENT_PASSWORD" {
  default = ""
}

variable "CTS_CLIENT_SECURITY_TOKEN" {
  default = ""
}

variable "CTS_LOGIN_URL" {
  default = ""
}

variable "CTS_DOMAIN" {
  default = ""
}

// dispatch-portal environment variables

variable "DISPATCH_PORTAL_SERVER_PORT" {
  default = ""
}

// hawkeye-bridge environment variables

variable "HAWKEYE_CLIENT_USERNAME" {
  default = ""
}

variable "HAWKEYE_CLIENT_PASSWORD" {
  default = ""
}

variable "HAWKEYE_BASE_URL" {
  default = ""
}

// last-contact-report environment variables

variable "LAST_CONTACT_RECIPIENT" {
  default = ""
}

// lit-bridge environment variables

variable "LIT_CLIENT_ID"{
  default = ""
}

variable "LIT_CLIENT_SECRET"{
  default = ""
}

variable "LIT_CLIENT_USERNAME"{
  default = ""
}

variable "LIT_CLIENT_PASSWORD"{
  default = ""
}

variable "LIT_CLIENT_SECURITY_TOKEN"{
  default = ""
}

variable "LIT_LOGIN_URL"{
  default = ""
}

variable "LIT_DOMAIN"{
  default = ""
}

// lumin-billing-report environment variables

variable "LUMIN_URI" {
  default = ""
}

variable "LUMIN_TOKEN" {
  default = ""
}

variable "CUSTOMER_NAME_BILLING_REPORT" {
  default = ""
}

variable "BILLING_RECIPIENT_REPORT" {
  default = ""
}

// nats-server environment variables

variable "NATS_SERVER_SEED_CLUSTER_PORT" {
  default = 5222
  type = number
  description = "NATS edge server cluster port"
}

variable "NATS_SERVER_SEED_CLIENTS_PORT" {
  default = "4222"
  type = string
  description = "Port for clients in NATS seed node"
}

variable "NATS_SERVER_SEED_CLUSTER_MODE" {
  default = "s"
  type = string
  description = "NATS seed node cluster mode"
}

// nats-server-1 environment variables

variable "NATS_SERVER_1_CLUSTER_PORT" {
  default = 5223
  type = number
  description = "NATS server 1 cluster port"
}

variable "NATS_SERVER_1_CLIENTS_PORT" {
  default = "4223"
  type = string
  description = "Port for clients in NATS seed node 1"
}

variable "NATS_SERVER_1_CLUSTER_MODE" {
  default = "n"
  type = string
  description = "NATS server 1 node cluster mode"
}

// nats-server-2 environment variables

variable "NATS_SERVER_2_CLUSTER_PORT" {
  default = 5224
  type = number
  description = "NATS server 2 cluster port"
}

variable "NATS_SERVER_2_CLIENTS_PORT" {
  default = "4224"
  type = string
  description = "Port for clients in NATS seed node 2"
}

variable "NATS_SERVER_2_CLUSTER_MODE" {
  default = "n"
  type = string
  description = "NATS server 2 node cluster mode"
}

// papertrail environment variables

variable PAPERTRAIL_HOST {
  type = string
  description = "Papertrail address to which the logs of the microservices with the send to papertrail flag will be sent"
  default = ""
}

variable PAPERTRAIL_PORT {
  type = number
  description = "Papertrail host to which the logs of the microservices with the send to papertrail flag will be sent"
  default = 0
}

// redis variables

variable "redis_node_type" {
  type = "map"
  default = {
    "production"  = "cache.m4.large"
    "dev"         = "cache.t2.micro"
  }
}

variable "redis_node_type_cache_for_microservices" {
  type = "map"
  default = {
    "production" = "cache.t2.small"
    "dev"        = "cache.t2.micro"
  }
}

// service-outage-monitor-1 environment variables

variable "SERVICE_OUTAGE_MONITOR_1_HOSTS" {
  type = string
  description = "Velocloud hosts for outage monitoring # 1"
}

variable "SERVICE_OUTAGE_MONITOR_1_HOSTS_FILTER" {
  type = string
  description = "Velocloud hosts filter for outage monitoring # 1"
}

// service-outage-monitor-2 environment variables

variable "SERVICE_OUTAGE_MONITOR_2_HOSTS" {
  type = string
  description = "Velocloud hosts for outage monitoring # 2"
}

variable "SERVICE_OUTAGE_MONITOR_2_HOSTS_FILTER" {
  type = string
  description = "Velocloud hosts filter for outage monitoring # 2"
}

// service-outage-monitor-3 environment variables

variable "SERVICE_OUTAGE_MONITOR_3_HOSTS" {
  type = string
  description = "Velocloud hosts for outage monitoring # 3"
}

variable "SERVICE_OUTAGE_MONITOR_3_HOSTS_FILTER" {
  type = string
  description = "Velocloud hosts filter for outage monitoring # 3"
}

// service-outage-monitor-4 environment variables

variable "SERVICE_OUTAGE_MONITOR_4_HOSTS" {
  type = string
  description = "Velocloud hosts for outage monitoring # 3"
}

variable "SERVICE_OUTAGE_MONITOR_4_HOSTS_FILTER" {
  type = string
  description = "Velocloud hosts filter for outage monitoring # 3"
}

// t7-bridge environment variables

variable "KRE_BASE_URL"{
  default = ""
}

variable "T7_BASE_URL"{
  default = ""
}

variable "T7_TOKEN"{
  default = ""
}

// velocloud-bridge environment variables

variable "VELOCLOUD_CREDENTIALS" {
  default = ""
}

variable "VELOCLOUD_VERIFY_SSL" {
  default = "yes"
}

variable "ALARMS_SUBSCRIPTIONS_EMAIL_ADDRESS" {
  type = "string"
  description = "Email addresses to send notifications generated by alarm of errors and exceptions detected in services"
  default = "xoan.mallon@intelygenz.com"
}

// desired tasks per microservice

variable "bruin_bridge_desired_tasks" {
  default = 2
  type = number
  description = "Number of desired tasks of microservice bruin-bridge"
}

variable "cts_bridge_desired_tasks" {
  default = 1
  type = number
  description = "Number of desired tasks of microservice cts-bridge"
}

variable "dispatch_portal_frontend_desired_tasks" {
  default = 1
  type = number
  description = "Number of desired tasks of microservice dispatch-portal-frontend"
}

variable "customer_cache_desired_tasks" {
  default = 1
  type = number
  description = "Number of desired tasks of microservice customer-cache"
}

variable "dispatch_portal_backend_desired_tasks" {
  default = 1
  type = number
  description = "Number of desired tasks of microservice dispatch-portal-backend"
}

variable "hawkeye_bridge_desired_tasks" {
  default = 1
  type = number
  description = "Number of desired tasks of microservice hawkeye-bridge"
}

variable "hawkeye_customer_cache_desired_tasks" {
  default = 1
  type = number
  description = "Number of desired tasks of microservice hawkeye-customer-cache"
}

variable "hawkeye_outage_monitor_desired_tasks" {
  default = 1
  type = number
  description = "Number of desired tasks of microservice hawkeye-outage-monitor"
}

variable "last_contact_report_desired_tasks" {
  default = 1
  type = number
  description = "Number of desired tasks of microservice last-contact-report"
}

variable "lit_bridge_desired_tasks" {
  default = 1
  type = number
  description = "Number of desired tasks of microservice lit-bridge"
}

variable "lumin_billing_report_desired_tasks" {
  default = 1
  type = number
  description = "Number of desired tasks of microservice lumin-billing-report"
}

variable "metrics_prometheus_desired_tasks" {
  default = 1
  type = number
  description = "Number of desired tasks of microservice metrics-prometheus"
}

variable "metrics_thanos_store_gateway_desired_tasks" {
  default = 1
  type = number
  description = "Number of desired tasks of microservice metrics-thanos-store-gateway"
}

variable "nats_server_desired_tasks" {
  default = 1
  type = number
  description = "Number of desired tasks of microservice nats-server"
}

variable "nats_server_1_desired_tasks" {
  default = 1
  type = number
  description = "Number of desired tasks of microservice nats-server-1"
}

variable "nats_server_2_desired_tasks" {
  default = 1
  type = number
  description = "Number of desired tasks of microservice nats-server-2"
}

variable "notifier_desired_tasks" {
  default = 1
  type = number
  description = "Number of desired tasks of microservice notifier"
}

variable "service_affecting_monitor_desired_tasks" {
  default = 1
  type = number
  description = "Number of desired tasks of microservice service-affecting-monitor"
}

variable "service_dispatch_monitor_desired_tasks" {
  default = 1
  type = number
  description = "Number of desired tasks of microservice service-dispatch-monitor"
}

variable "service_outage_monitor_1_desired_tasks" {
  default = 0
  type = number
  description = "Number of desired tasks of microservice service-outage-monitor # 1"
}

variable "service_outage_monitor_2_desired_tasks" {
  default = 0
  type = number
  description = "Number of desired tasks of microservice service-outage-monitor # 2"
}

variable "service_outage_monitor_3_desired_tasks" {
  default = 0
  type = number
  description = "Number of desired tasks of microservice service-outage-monitor # 3"
}

variable "service_outage_monitor_4_desired_tasks" {
  default = 0
  type = number
  description = "Number of desired tasks of microservice service-outage-monitor # 4"
}

variable "service_outage_monitor_triage_desired_tasks" {
  default = 0
  type = number
  description = "Number of desired tasks of microservice service-outage-monitor for triage"
}

variable "sites_monitor_desired_tasks" {
  default = 1
  type = number
  description = "Number of desired tasks of microservice sites-monitor"
}

variable "tnba_monitor_desired_tasks" {
  default = 1
  type = number
  description = "Number of desired tasks of microservice tnba-monitor"
}

variable "tnba_feedback_desired_tasks" {
  default = 1
  type = number
  description = "Number of desired tasks of microservice tnba-feedback"
}

variable "t7_bridge_desired_tasks" {
  default = 1
  type = number
  description = "Number of desired tasks of microservice t7-bridge"
}

variable "velocloud_bridge_desired_tasks" {
  default = 5
  type = number
  description = "Number of desired tasks of microservice velocloud-bridge"
}

// task-definition output per microservices

variable "bruin-bridge-task-definition-json" {
  type = string
  description = "Task definition arn output in rendered json for bruin-bridge"
  default = "/tmp/bruin-bridge-task-definition.json"
}

variable "cts-bridge-task-definition-json" {
  type = string
  description = "Task definition arn output in rendered json for CTS-bridge"
  default = "/tmp/cts-bridge-task-definition.json"
}

variable "customer-cache-task-definition-json" {
  type = string
  description = "Task definition arn output in rendered json for customer-cache"
  default = "/tmp/customer-cache-task-definition.json"
}

variable "dispatch-portal-backend-task-definition-json" {
  type = string
  description = "Task definition arn output in rendered json for CTS-bridge"
  default = "/tmp/dispatch-portal-backend-task-definition.json"
}

variable "hawkeye-bridge-task-definition-json" {
  type = string
  description = "Task definition arn output in rendered json for hawkeye-bridge"
  default = "/tmp/hawkeye-bridge-task-definition.json"
}

variable "hawkeye-customer-cache-task-definition-json" {
  type = string
  description = "Task definition arn output in rendered json for hawkeye-customer-cache"
  default = "/tmp/hawkeye-customer-cache-task-definition.json"
}

variable "hawkeye-outage-monitor-task-definition-json" {
  type = string
  description = "Task definition arn output in rendered json for hawkeye-outage-monitor"
  default = "/tmp/hawkeye-outage-monitor-task-definition.json"
}

variable "lit-bridge-task-definition-json" {
  type = string
  description = "Task definition arn output in rendered json for lit-bridge"
  default = "/tmp/lit-bridge-task-definition.json"
}

variable "metrics-prometheus-task-definition-json" {
  type = string
  description = "Task definition arn output in rendered json for bruin-bridge"
  default = "/tmp/metrics-prometheus-task-definition.json"
}

variable "nats-server-task-definition-json" {
  type = string
  description = "Task definition arn output in rendered json for nats-server"
  default = "/tmp/nats-server-taks-definition.json"
}

variable "notifier-task-definition-json" {
  type = string
  description = "Task definition arn output in rendered json for notifier"
  default = "/tmp/notifier-task-definition.json"
}

variable "t7-bridge-task-definition-json" {
  type = string
  description = "Task definition arn output in rendered json for t7-bridge"
  default = "/tmp/t7-bridge-task-definition.json"
}

variable "velocloud-bridge-task-definition-json" {
  type = string
  description = "Task definition arn output in rendered json for velocloud-bridge"
  default = "/tmp/velocloud-bridge-task-definition.json"
}

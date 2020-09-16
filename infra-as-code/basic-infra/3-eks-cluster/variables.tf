variable "map_users" {
  description = "Additional IAM users to add to the aws-auth configmap."
  type = list(object({
    userarn  = string
    username = string
    groups   = list(string)
  }))

  default = [
    {
      userarn  = "arn:aws:iam::374050862540:user/angel.costales"
      username = "angel.costales"
      groups   = ["system:masters"]
    }
  ]
}

variable "worker_node_instance_type" {
  type = map(string)

  default = {
    "dev"         = "m5.large"
    "production"  = "m5.large"
  }
}

# helm charts variables

variable "EXTERNAL_DNS_HELM_CHART_VERSION" {
  default     = "4.8.6"
  description = "Helm chart version used for external-dns"
}

variable "INGRESS_NGINX_HELM_CHART_VERSION" {
  default     = "3.21.0"
  description = "Helm chart version used for ingress-nginx"
}

variable "METRICS_SERVER_VERSION" {
  default     = "0.4.2"
  description = "Version of metrics server release to install in the EKS cluster"
}

variable "RELOADER_CHART_VERSION" {
  default     = "0.0.81"
  description = "Helm chart version used for reloader"
}

variable "WHITELISTED_IPS" {
  type        = list(string)
  default     = [""]
  description = "Allowed IPs to access Load Balancer created by nginx ingress controller"
}

# grafana variables

variable "GRAFANA_ADMIN_USER" {
  default     = ""
  description = "Grafana admin user"
}

variable "GRAFANA_ADMIN_PASSWORD" {
  default     = ""
  description = "Grafana admin password"
}
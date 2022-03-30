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
    "dev"         = "m6a.large"
    "production"  = "m6a.large"
  }
}

# helm charts variables

variable "CLUSTER_AUTOSCALER_HELM_CHART_VERSION" {
  default     = "9.4.0"
  description = "Helm chart version used for cluster-autoscaler"
}

variable "CHARTMUSEUM_HELM_CHART_VERSION" {
  default     = "3.3.0"
  description = "Helm chart version used for chartmuseum"
}

variable "EXTERNAL_DNS_HELM_CHART_VERSION" {
  default     = "4.8.6"
  description = "Helm chart version used for external-dns"
}

variable "EXTERNAL_SECRETS_HELM_CHART_VERSION" {
  default     = "0.4.1"
  description = "Helm chart version used for external-secrets"
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

variable "WHITELISTED_IPS_OREILLY" {
  type        = list(string)
  default     = [""]
  description = "Allowed IPs to access Load Balancer created for oreilly client"
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

variable "CHARTMUSEUM_USER" {
  default     = ""
  description = "Chartmuseum basic auth user"
}

variable "CHARTMUSEUM_PASSWORD" {
  default     = ""
  description = "Chartmuseum basic auth password"
}

variable "ENABLE_FLUENT_BIT" {
  default     = "false"
  description = "If set to true, enable fluent-bit required components"
}

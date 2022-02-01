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

variable "CERT_MANAGER_HELM_CHART_VERSION" {
  default     = "1.2.0"
  description = "Helm chart version used for cert-manager"
}

variable "EXTERNAL_DNS_HELM_CHART_VERSION" {
  default     = "4.8.6"
  description = "Helm chart version used for external-dns"
}

variable "HOSTPATH_HELM_CHART_VERSION" {
  default     = "0.2.9"
  description = "Helm chart version used for hostpath"
}

variable "LOCAL_PATH_PROVISIONER_HELM_CHART_VERSION" {
  default     = "0.0.21"
  description = "Helm chart version used for local-path-provisioner"
}

variable "INGRESS_NGINX_HELM_CHART_VERSION" {
  default     = "3.21.0"
  description = "Helm chart version used for ingress-nginx"
}

variable "METRICS_SERVER_VERSION" {
  default     = "0.4.2"
  description = "Version of metrics server release to install in the EKS cluster"
}

variable "WHITELISTED_IPS" {
  type        = list(string)
  default     = [""]
  description = "Allowed IPs to access Load Balancer created by nginx ingress controller"
}
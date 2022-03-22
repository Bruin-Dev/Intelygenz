variable "METRICS_SERVER_HELM_CHART_VERSION" {
  default     = "3.8.2"
  description = "Helm chart version used for metrics-server"
}

variable "EXTERNAL_DNS_HELM_CHART_VERSION" {
  default     = "6.2.1"
  description = "Helm chart version used for external-dns"
}

variable "INGRESS_NGINX_HELM_CHART_VERSION" {
  default     = "4.0.13"
  description = "Helm chart version used for ingress-nginx"
}

variable "DESCHEDULER_HELM_CHART_VERSION" {
  default     = "0.23.2"
  description = "Helm chart version used for descheduler"
}

variable "EBS_CSI_HELM_CHART_VERSION" {
  default     = "2.6.4"
  description = "Helm chart version used for aws-ebs-csi-driver"
}


### EKS ADMIN
variable "EKS_CLUSTER_ADMIN_IAM_USER_NAME" {
  default     = "angel.costales"
  description = "IAM user name to admin cluster"
}


### EKS ADDONS
variable "EKS_ADDON_VPC_CNI_VERSION" {
  default     = "v1.10.2-eksbuild.1"
  description = "EKS addon version used for VPC CNI"
}

variable "EKS_ADDON_EBS_CSI_VERSION" {
  default     = "v1.4.0-eksbuild.preview"
  description = "EKS addon version used for EBS CSI"
}

variable "EKS_ADDON_KUBE_PROXY_VERSION" {
  default     = "v1.21.2-eksbuild.2"
  description = "EKS addon version used for KUBE-PROXY"
}

variable "EKS_ADDON_COREDNS_VERSION" {
  default     = "v1.8.4-eksbuild.1"
  description = "EKS addon version used for COREDNS"
}


variable "WHITELISTED_IPS" {
  type        = list(string)
  default     = [""]
  description = "Allowed IPs to access Load Balancer created by nginx ingress controller"
}
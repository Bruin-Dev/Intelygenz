variable "eks_developer_users" {
  type    = list(string)
  default = [
    "brandon.samudio",
    "daniel.fernandez",
    "joseluis.vega",
    "sancho.munoz",
    "xoan.mallon.developer"
  ]
}

variable "eks_devops_users" {
  description = "List of users with devops role access in EKS cluster"
  type    = list(string)
  default = [
    "alberto.iglesias",
    "angel.luis.piquero",
    "xoan.mallon",
    "jose.bustos"
  ]
}

variable "EKS_CLUSTER_NAME" {
  description = "EKS Cluster name to obtain data"
  default = ""
}
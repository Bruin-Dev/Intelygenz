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
    "angel.costales",
    "angel.luis.piquero",
    "xoan.mallon.devops"
  ]
}
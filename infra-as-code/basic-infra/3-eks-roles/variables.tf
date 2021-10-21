variable "eks_developer_users" {
  type    = list(string)
  default = [
    "brandon.samudio",
    "joseluis.vega",
    "marc.vivancos",
    "ricardo.hortelano",
    "juancarlos.gomez",
    "julia.hossu",
    "sergio.delpuerto"
  ]
}

variable "eks_devops_users" {
  description = "List of users with devops role access in EKS cluster"
  type    = list(string)
  default = [
    "alberto.iglesias",
    "angel.luis.piquero",
    "alejandro.aceituna",
    "daniel.fernandez",
  ]
}

variable "EKS_CLUSTER_NAME" {
  description = "EKS Cluster name to obtain data"
  default = ""
}
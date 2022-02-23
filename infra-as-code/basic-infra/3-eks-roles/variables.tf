variable "eks_developer_users" {
  type    = list(string)
  default = [
    "some.user",
    "foo.var"
  ]
}

variable "eks_ops_users" {
  description = "List of users with devops role access in EKS cluster"
  type    = list(string)
  default = [
    "jon.du"
  ]
}
variable "eks_devops_users" {
  description = "List of users with devops role access in EKS cluster"
  type    = list(string)
  default = [
    "foo.vartwo"
  ]
}

variable "EKS_CLUSTER_NAME" {
  description = "EKS Cluster name to obtain data"
  default = ""
}
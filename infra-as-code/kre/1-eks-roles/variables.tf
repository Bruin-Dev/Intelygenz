variable "eks_developer_users" {
  description = "List of users with developer role access in EKS cluster"
  type    = list(string)
  default = [
    "some.user",
    "foo.var"
  ]
}

variable "eks_devops_users" {
  description = "List of users with devops role access in EKS cluster"
  type    = list(string)
  default = [
    "foo.vartwo"
  ]
}

variable "eks_ops_users" {
  description = "List of users with ops role access in EKS cluster"
  type    = list(string)
  default = [
    "jon.du"
  ]
}


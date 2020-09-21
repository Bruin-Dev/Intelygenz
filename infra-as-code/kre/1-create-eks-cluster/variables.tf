variable "map_users" {
  description = "Additional IAM users to add to the aws-auth configmap."
  type = list(object({
    userarn  = string
    username = string
    groups   = list(string)
  }))

  default = [
    {
      userarn  = "arn:aws:iam::374050862540:user/xoan.mallon"
      username = "xoan.mallon"
      groups   = ["system:masters"]
    }
  ]
}
# Data from EKS
data "aws_instances" "eks_workers_instances" {

  filter {
    name   = "tag:Name"
    values = [
      local.eks_workers_security_group_name
    ]
  }
  filter {
    name   = "tag:Environment"
    values = [
      var.CURRENT_ENVIRONMENT
    ]
  }

  instance_state_names = ["running"]
}

# Data from KRE
data "aws_security_group" "kre_elb_security_group" {
  filter {
    name   = local.kre_nginx_ingress_sg_tag_key
    values = [
      local.kre_nginx_ingress_sg_tag_value
    ]
  }
  filter {
    name = "group-name"
    values = [
      local.kre_elb_sg_name
    ]
  }
}

data "aws_security_group" "kre_workers_security_group" {
  filter {
    name   = "tag:Name"
    values = [
      local.kre_workers_security_group_name
    ]
  }
  filter {
    name = "tag:Environment"
    values = [
      var.CURRENT_ENVIRONMENT
    ]
  }
}
module "mettel-automation-eks-cluster" {
  source          = "terraform-aws-modules/eks/aws"
  cluster_name    = local.cluster_name
  cluster_version = local.k8s_version
  subnets         = local.subnets
  vpc_id          = local.vpc_id

  worker_groups = [
    {
      name = "worker_node"
      instance_type = local.worker_nodes_instance_type
      asg_min_size  = 4
      asg_max_size  = 5
      key_name = aws_key_pair.aws_key_pair.key_name
      userdata_template_file = local.eks-node-userdata
    }
  ]

   map_users     = var.map_users

  tags = {
    Environment  = terraform.workspace
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
  }

  version = "12.2.0"
}
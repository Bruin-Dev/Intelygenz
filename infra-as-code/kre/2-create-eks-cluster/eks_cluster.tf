module "mettel-automation-eks-cluster" {
  source                          = "terraform-aws-modules/eks/aws"
  cluster_name                    = local.cluster_name
  cluster_version                 = local.k8s_version
  subnets                         = local.subnets
  vpc_id                          = local.vpc_id
  write_kubeconfig                = false
  worker_ami_name_filter          = local.eks_worker_ami_name_filter
  worker_ami_owner_id             = local.eks_worker_ami_owner_id
  cluster_endpoint_private_access = true

  worker_groups = [
    {
      name                    = "worker_node"
      instance_type           = local.worker_nodes_instance_type
      asg_min_size            = local.min_worker_nodes
      asg_desired_capacity    = local.min_worker_nodes
      asg_max_size            = local.max_worker_nodes
      key_name                = aws_key_pair.aws_key_pair.key_name
      userdata_template_file  = local.eks-node-userdata
      root_volume_type        = local.eks_worker_root_volume_type
    }
  ]

  map_users     = var.map_users

  tags = {
    Environment  = terraform.workspace
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
  }

  version = "15.2.0"
}


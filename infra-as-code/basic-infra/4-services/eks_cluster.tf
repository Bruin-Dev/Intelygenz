/*module "mettel-automation-eks-cluster" {
  count = 0
  source                          = "terraform-aws-modules/eks/aws"
  cluster_name                    = local.cluster_name
  cluster_version                 = local.k8s_version
  subnets                         = data.aws_subnet_ids.mettel-automation-private-subnets.ids
  vpc_id                          = data.aws_vpc.mettel-automation-vpc.id
  write_kubeconfig                = false
  worker_ami_name_filter          = local.eks_worker_ami_name_filter
  worker_ami_owner_id             = local.eks_worker_ami_owner_id
  cluster_endpoint_private_access = true

  worker_groups = [
    {
      name                  = "worker_node"
      instance_type         = var.worker_node_instance_type[var.CURRENT_ENVIRONMENT]
      asg_min_size          = local.min_worker_nodes
      asg_desired_capacity  = local.min_worker_nodes
      asg_max_size          = local.max_worker_nodes
      key_name              = aws_key_pair.aws_key_pair.key_name
      root_volume_type      = local.eks_worker_root_volume_type
    }
  ]

  map_users     = var.map_users

  tags = merge(local.common_tags, {
    Name         = local.cluster_name
    "k8s.io/cluster-autoscaler/enabled" = "true"
    "k8s.io/cluster-autoscaler/${local.cluster_name}" = "true"
  })

  version = "17.1.0"
} */

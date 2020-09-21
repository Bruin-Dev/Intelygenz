locals  {
  // EKS cluster local variables
  cluster_name = "${var.common_info.project}-${var.CURRENT_ENVIRONMENT}"
  k8s_version = "1.17"
  worker_nodes_instance_type = "t3.medium"

  // EKS cluster access key local variables
  ssh_key_name = "${var.common_info.project}-${var.CURRENT_ENVIRONMENT}-eks-key"

  // EKS node userdata to install EFS
  eks-node-userdata = <<USERDATA
      #!/bin/bash
      set -o xtrace
      /etc/eks/bootstrap.sh --apiserver-endpoint '${module.mettel-automation-eks-cluster.cluster_endpoint}' --b64-cluster-ca '${data.aws_eks_cluster.cluster.certificate_authority.0.data}' '${local.cluster_name}'
      mkdir -p /mnt/efs/${local.cluster_name}
      yum install amazon-efs-utils -y
      echo "${aws_efs_file_system.efs_file_system.dns_name}:/ /mnt/efs/${local.cluster_name} efs tls,_netdev" >> /etc/fstab
      mount -a -t efs defaults
  USERDATA

  // S3 bucket with EKS cluster info local variables
  bucket_name = "${var.common_info.project}-${var.CURRENT_ENVIRONMENT}-eks"

  // public subnets used in cluster
  subnets         = [
    data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-public-1a.id,
    data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-public-1b.id
  ]

  // VPC id of VPC used in cluster
  vpc_id = data.terraform_remote_state.tfstate-network-resources.outputs.vpc_automation_id

  // default region used in AWS
  aws_default_region = "us-east-1"

  // kubeconfig local store
  kubeconfig_dir = "/tmp/kubeconfig"

  // ALB from nginx ingress deployed output
  alb_from_nginx_ingress = "/tmp/alb_from_nginx_ingress"

  // kre record alias name
  kre_record_alias_name = "*.kre-${var.CURRENT_ENVIRONMENT}.mettel-automation.net."

  // kre hosted zone name
  kre_record_hosted_zone_name = "kre-${var.CURRENT_ENVIRONMENT}.mettel-automation.net."
}

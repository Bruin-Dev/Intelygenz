locals {
  // kre local vars
  kre_nginx_ingress_sg_tag_key = var.CURRENT_ENVIRONMENT == "dev" ? "tag:kubernetes.io/cluster/${var.common_info.project}-kre-dev" : "tag:kubernetes.io/cluster/${var.common_info.project}-kre"
  kre_nginx_ingress_sg_tag_value = "owned"
  kre_elb_sg_name = "k8s-elb-*"
  kre_workers_security_group_name = var.CURRENT_ENVIRONMENT == "dev" ? "${var.common_info.project}-kre-${var.CURRENT_ENVIRONMENT}-eks_worker_sg" : "${var.common_info.project}-kre-eks_worker_sg"

  // eks local vars
  eks_workers_security_group_name = var.CURRENT_ENVIRONMENT == "dev" ? "${var.common_info.project}-${var.CURRENT_ENVIRONMENT}-worker_node-eks_asg" : "${var.common_info.project}-worker_node-eks_asg"

  eks_cidrs_eips = formatlist("%s/32", data.aws_instances.eks_workers_instances.public_ips)
}
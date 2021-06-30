resource "aws_security_group_rule" "calls_from_ingress_elb_to_eks_worker_nodes" {
  description               = "Allow calls from ELB of ingress-nginx to EKS worker nodes"
  type                      = "ingress"
  from_port                 = 1025
  to_port                   = 65535
  protocol                  = "tcp"
  security_group_id         = data.aws_security_group.eks_nodes_security_group.id
  source_security_group_id  = data.aws_security_group.elb_ingress_nginx_eks_security_group.id

  depends_on = [
    module.mettel-automation-eks-cluster,
    helm_release.ingress-nginx
  ]
}
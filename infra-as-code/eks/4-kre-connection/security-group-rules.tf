resource "aws_security_group_rule" "allow_environment_calls_from_eks_to_kre_elb" {
  description       = "Allow calls from EC2 instances of EKS cluster to KRE ELB"
  type              = "ingress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  security_group_id = data.aws_security_group.kre_elb_security_group.id
  cidr_blocks       = local.eks_cidrs_eips
}
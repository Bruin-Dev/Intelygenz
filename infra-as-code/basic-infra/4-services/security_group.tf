resource "aws_security_group_rule" "calls_from_ingress_elb_to_eks_worker_nodes" {
  description               = "Allow calls from ELB of ingress-nginx to EKS worker nodes"
  type                      = "ingress"
  from_port                 = 1025
  to_port                   = 65535
  protocol                  = "tcp"
  security_group_id         = data.aws_security_group.eks_nodes_security_group.id
  source_security_group_id  = data.aws_security_group.elb_ingress_nginx_eks_security_group.id

  depends_on = [
    //module.mettel-automation-eks-cluster,
    helm_release.ingress-nginx
  ]
}

resource "aws_security_group" "links_metrics_api_oreilly" {
  name = "${var.CURRENT_ENVIRONMENT}-links-metrics-oreilly-whitelisted-access"
  description = "links metrics api security group to allow clients IPs whited list"
  vpc_id      = data.aws_vpc.mettel-automation-vpc.id

  ingress {
      description      = "Allowed IP to access to 443 Oreilly service"
      from_port        = 443
      to_port          = 443
      protocol         = "tcp"
      cidr_blocks      = var.WHITELISTED_IPS_OREILLY
    }

  ingress {
      description      = "Allowed IP to access to 80 Oreilly service"
      from_port        = 80
      to_port          = 80
      protocol         = "tcp"
      cidr_blocks      = var.WHITELISTED_IPS_OREILLY
    }

  egress {
      from_port        = 0
      to_port          = 0
      protocol         = "-1"
      cidr_blocks      = ["0.0.0.0/0"]
      ipv6_cidr_blocks = ["::/0"]
    }

  tags = {
    Name         = "${var.CURRENT_ENVIRONMENT} Oreilly whitelisted IPs access"
    Environment  = var.CURRENT_ENVIRONMENT
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
  }
}
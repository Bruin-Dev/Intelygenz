module "mettel-automation-eks-cluster" {
  source = "terraform-aws-modules/eks/aws"
  version = "18.11.0"

  cluster_name                    = local.cluster_name
  cluster_version                 = local.k8s_version
  cluster_endpoint_private_access = true
  cluster_endpoint_public_access  = true
  enable_irsa                     = true

  cluster_encryption_config = [{
    provider_key_arn = aws_kms_key.kms_key.arn
    resources        = ["secrets"]
  }]

  vpc_id     = local.vpc_id
  subnet_ids = local.subnets

  # Extend cluster security group rules
  cluster_security_group_additional_rules = {
    egress_nodes_ephemeral_ports_tcp = {
      description                = "To node 1025-65535"
      protocol                   = "tcp"
      from_port                  = 1025
      to_port                    = 65535
      type                       = "egress"
      source_node_security_group = true
    }
  }

  # Extend node-to-node security group rules
  node_security_group_additional_rules = {
    ingress_self_all = {
      description = "Node to node all ports/protocols"
      protocol    = "-1"
      from_port   = 0
      to_port     = 0
      type        = "ingress"
      self        = true
    }
    ingress_cluster_all = {
      description                   = "Cluster to node all ports/protocols"
      protocol                      = "-1"
      from_port                     = 0
      to_port                       = 0
      type                          = "ingress"
      source_cluster_security_group = true
    }
    egress_all = {
      description      = "Node all egress"
      protocol         = "-1"
      from_port        = 0
      to_port          = 0
      type             = "egress"
      cidr_blocks      = ["0.0.0.0/0"]
      ipv6_cidr_blocks = ["::/0"]
    }
  }

  self_managed_node_group_defaults = {
    use_name_prefix          = true
    create_iam_role          = true
    iam_role_use_name_prefix = true
    disk_size                = local.volume_size
    ami_id                   = data.aws_ami.eks_worker_ami_name_filter.id
    key_name                 = aws_key_pair.aws_key_pair.key_name
    subnet_ids               = local.subnets

    pre_bootstrap_user_data = <<-EOT
    export CONTAINER_RUNTIME="containerd"
    export USE_MAX_PODS=false
    EOT

    post_bootstrap_user_data = <<-EOT
    echo "you are free little kubelet!"
    EOT 

    ebs_optimized          = true
    enable_monitoring      = true
    cloudwatch_log_group_retention_in_days = 30

    block_device_mappings = {
      xvda = {
        device_name = "/dev/xvda"
        ebs = {
          delete_on_termination = true
          encrypted             = false
          # kms_key_id            = aws_kms_key.kms_key.arn
          volume_size           = local.volume_size
          volume_type           = local.eks_worker_root_volume_type
        }

      }
    }
  }

  self_managed_node_groups = {

    general-node = {
      name                 = "${local.cluster_name}-general-node"
      instance_type        = local.general_instance_type
      bootstrap_extra_args = "--kubelet-extra-args '${local.max-pods-per-node}'"

      min_size     = local.min-general-worker-nodes
      max_size     = local.max-general-worker-nodes
      desired_size = local.min-general-worker-nodes

      iam_role_name            = "general-role"
      iam_role_description     = "general-role"
      
      iam_role_tags = {
        Purpose = "general-role"
      }
      iam_role_additional_policies = [
        "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
      ]
    }

    mongo-node = {

      name                 = "${local.cluster_name}-mongo-node"
      instance_type        = local.special_instance_type
      bootstrap_extra_args = "--kubelet-extra-args '${local.max-pods-per-node} --node-labels=dedicated=mongo --register-with-taints=dedicated=mongo:NoSchedule'"

      # at this moment we only use 1 node, so force to use only one AZ for the EBS storage dependecy
      subnet_ids   = [local.subnet_public_1a]

      min_size     = local.min-mongo-worker-nodes
      max_size     = local.max-mongo-worker-nodes
      desired_size = local.min-mongo-worker-nodes

      iam_role_name            = "mongo-role"
      iam_role_description     = "mongo-role"
      iam_role_tags = {
        Purpose = "mongo-role"
      }
      iam_role_additional_policies = [
        "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
      ]
    }

    influx-node = {
      name                 = "${local.cluster_name}-influx-node"
      instance_type        = local.special_instance_type
      bootstrap_extra_args = "--kubelet-extra-args '--max-pods=110 --node-labels=dedicated=influx --register-with-taints=dedicated=influx:NoSchedule'"

      # at this moment we only use 1 node, so force to use only one AZ for the EBS storage dependecy
      subnet_ids   = [local.subnet_public_1b]

      min_size     = local.min-influx-worker-nodes
      max_size     = local.max-influx-worker-nodes
      desired_size = local.min-influx-worker-nodes

      iam_role_name            = "influx-role"
      iam_role_description     = "influx-role"

      iam_role_tags = {
        Purpose = "influx-role"
      }
      iam_role_additional_policies = [
        "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
      ]
    }
  }

  tags = merge(var.common_info, {
    name         = local.cluster_name
    Environment  = terraform.workspace
    "k8s.io/cluster-autoscaler/enabled" = "true"
    "k8s.io/cluster-autoscaler/${local.cluster_name}" = "true"
  })
}

# from eks module version 18.x the module drop support for aws-auth configmap manage in self_managed_node_groups.
# Workaround: how to add iam_roles from self_managed_node_groups to aws-auth configmap on eks module 18.x:
# https://github.com/terraform-aws-modules/terraform-aws-eks/issues/1802
# In summary, we catch the data for eks managed nodes from "aws_auth_configmap_yaml" that have all the roles from all nodes and additionally include the iam role that we want to admin the cluster
# We use "kubectl" provider because "kubernetes" provider doesn't allow create the aws-auth file.

locals {
  aws_auth_configmap_yaml = <<-EOT
    ${chomp(module.mettel-automation-eks-cluster.aws_auth_configmap_yaml)}
      mapUsers: |
        - groups:
          - system:masters
          userarn: arn:aws:iam::${data.aws_caller_identity.current.account_id}:user/${var.EKS_CLUSTER_ADMIN_IAM_USER_NAME}
          username: ${var.EKS_CLUSTER_ADMIN_IAM_USER_NAME}
  EOT
}

data "http" "wait_for_cluster" {
  url            = format("%s/healthz", module.mettel-automation-eks-cluster.cluster_endpoint)
  ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority.0.data)
  timeout        = 1200

  depends_on = [
    module.mettel-automation-eks-cluster
  ]
}

resource "kubectl_manifest" "aws_auth" {
  yaml_body = <<YAML
apiVersion: v1
kind: ConfigMap
metadata:
  labels:
    app.kubernetes.io/managed-by: Terraform
  name: aws-auth
  namespace: kube-system
${local.aws_auth_configmap_yaml}
YAML

  depends_on = [
    module.mettel-automation-eks-cluster,
    data.http.wait_for_cluster
  ]
}



## EKS addons

#########################################
### VPC CNI (Container Network Interface)
### to support native VPC networking
#########################################

resource "aws_eks_addon" "vpc_cni" {

  cluster_name      = module.mettel-automation-eks-cluster.cluster_id
  addon_name        = "vpc-cni"
  resolve_conflicts = "OVERWRITE"
  addon_version     = var.EKS_ADDON_VPC_CNI_VERSION

  tags = merge(var.common_info, {
    name = "vpc-cni"
  })

  depends_on = [
    kubectl_manifest.aws_auth,
    module.vpc_cni_irsa,
  ]
}

module "vpc_cni_irsa" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"

  role_name             = "${local.cluster_name}_vpc_cni"
  attach_vpc_cni_policy = true
  vpc_cni_enable_ipv4   = true

  oidc_providers = {
    main = {
      provider_arn               = module.mettel-automation-eks-cluster.oidc_provider_arn
      namespace_service_accounts = ["kube-system:aws-node"]
    }
  }

  tags = merge(var.common_info, {
    name         = "vpc_cni_irsa"
  })
}


################################################
### kube-proxy
### to enables network communication to the pods
################################################

resource "aws_eks_addon" "kube_proxy" {

  cluster_name      = module.mettel-automation-eks-cluster.cluster_id
  addon_name        = "kube-proxy"
  resolve_conflicts = "OVERWRITE"
  addon_version     = var.EKS_ADDON_KUBE_PROXY_VERSION

  tags = merge(var.common_info, {
    name = "kube-proxy"
  })

  depends_on = [
    kubectl_manifest.aws_auth
  ]
}


###################################
### coredns
### to serve Kubernetes cluster DNS
###################################

resource "aws_eks_addon" "coredns" {

  cluster_name      = module.mettel-automation-eks-cluster.cluster_id
  addon_name        = "coredns"
  resolve_conflicts = "OVERWRITE"
  addon_version     = var.EKS_ADDON_COREDNS_VERSION

  tags = merge(var.common_info, {
    name = "coredns"
  })

  depends_on = [
    kubectl_manifest.aws_auth
  ]
}

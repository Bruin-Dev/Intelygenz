resource "aws_security_group" "security_group_efs" {
  name        = "${local.cluster_name}-efs"
  description = "Security group for efs "
  vpc_id      = data.terraform_remote_state.tfstate-network-resources.outputs.vpc_automation_id

  ingress {
    from_port = 2049
    to_port   = 2049
    protocol  = "TCP"
    security_groups = [module.mettel-automation-eks-cluster.worker_security_group_id]
  }
}

resource "aws_efs_file_system" "efs_file_system" {
  tags = map(
     "Name", local.cluster_name,
     "kubernetes.io/cluster/${local.cluster_name}", "owned",
    )
}

resource "aws_efs_mount_target" "efs_mount_target" {
  file_system_id = aws_efs_file_system.efs_file_system.id
  count = 2
  subnet_id = element(local.subnets,count.index)
  security_groups = [aws_security_group.security_group_efs.id]
}

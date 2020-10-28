resource "tls_private_key" "tls_private_key_eks" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "aws_key_pair" {
  key_name   = local.ssh_key_name
  public_key = tls_private_key.tls_private_key_eks.public_key_openssh

  tags = {
    Environment  = terraform.workspace
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
  }
}

resource "aws_s3_bucket_object" "pem_file" {
  bucket  = local.bucket_name
  key     = "${local.ssh_key_name}.pem"
  content = tls_private_key.tls_private_key_eks.private_key_pem

  tags = {
    Name          = "${local.cluster_name}.pem"
    Environment   = terraform.workspace
    Project       = var.common_info.project
    Provisioning  = var.common_info.provisioning
  }
}

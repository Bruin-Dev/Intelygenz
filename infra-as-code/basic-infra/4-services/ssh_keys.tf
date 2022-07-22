resource "tls_private_key" "tls_private_key_eks" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "aws_key_pair" {
  key_name   = local.ssh_key_name
  public_key = tls_private_key.tls_private_key_eks.public_key_openssh
}
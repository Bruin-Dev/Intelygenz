resource "aws_s3_bucket_object" "pem_file" {
  bucket  = local.bucket_name
  key     = "${local.ssh_key_name}.pem"
  content = tls_private_key.tls_private_key_eks.private_key_pem

  tags = merge(local.common_tags, {
    Name    = "${local.cluster_name}.pem"
  })
}
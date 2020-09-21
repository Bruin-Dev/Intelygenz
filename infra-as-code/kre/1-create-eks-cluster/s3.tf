resource "aws_s3_bucket_object" "config_map_aws_auth" {
  bucket  = local.bucket_name
  key     = "config_map_aws_auth"
  content = local.config_map_aws_auth

  tags = {
    Name    = "config_map_aws_auth"
  }
}

resource "aws_s3_bucket_object" "kubeconfig" {
  bucket  = local.bucket_name
  key     = "kubeconfig"
  content = local.kubeconfig

  tags = {
    Name    = "kubeconfig"
  }

  depends_on = [module.mettel-automation-eks-cluster]
}


resource "aws_s3_bucket_object" "envs_file" {
  bucket  = local.bucket_name
  key     = "envs_file"
  content = local.envs_file

  tags = {
    Name    = "envs_file"
  }
}
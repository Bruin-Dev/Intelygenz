resource "aws_s3_bucket_object" "config_map_aws_auth" {
  bucket  = local.bucket_name
  key     = "config_map_aws_auth"
  content = local.config_map_aws_auth

  tags = {
    Name    = "config_map_aws_auth"
  }
}

resource "aws_s3_bucket_object" "envs_file" {
  bucket  = local.bucket_name
  key     = "envs_file"
  content = local.envs_file

  tags = {
    Name    = "envs_file"
  }
}
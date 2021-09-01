# This object is created here because we want the option to destroy and recreate the entire EKS cluster, 
# if we leave the bucket in the "2-eks-cluster" folder, when we redeploy de pipeline it will fail because 
# the bucket requires a long time to be deleted and recreated with the same name (10 hours or more).

resource "aws_s3_bucket" "bucket_eks_cluster" {
  bucket        = local.bucket_name
  acl           = "private"
  force_destroy = true

  tags = {
    Name         = local.bucket_name
    Environment  = var.CURRENT_ENVIRONMENT
    Project      = var.common_info.project
    Provisioning = var.common_info.provisioning
  }
}
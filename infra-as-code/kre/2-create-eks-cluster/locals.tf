locals  {
  // EKS cluster local variables
  cluster_name                = var.CURRENT_ENVIRONMENT == "dev" ? "${var.common_info.project}-${var.CURRENT_ENVIRONMENT}" : var.common_info.project
  k8s_version                 = "1.21"
  eks_worker_root_volume_type = "gp3"
  volume_size                 = var.CURRENT_ENVIRONMENT == "dev" ? 50 : 100
  
  special_instance_type       = var.CURRENT_ENVIRONMENT == "dev" ? "m6a.large" : "m6i.xlarge" 
  general_instance_type       = var.CURRENT_ENVIRONMENT == "dev" ? "m6a.large" : "m6a.xlarge" 

  min-general-worker-nodes = var.CURRENT_ENVIRONMENT == "dev" ? 3 : 3
  max-general-worker-nodes = var.CURRENT_ENVIRONMENT == "dev" ? 4 : 6

  min-mongo-worker-nodes = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 1
  max-mongo-worker-nodes = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 2

  min-influx-worker-nodes = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 1
  max-influx-worker-nodes = var.CURRENT_ENVIRONMENT == "dev" ? 1 : 2

  // check documentation: https://github.com/awslabs/amazon-eks-ami/blob/master/files/eni-max-pods.txt
  max-pods-per-node = var.CURRENT_ENVIRONMENT == "dev" ? "--max-pods=29" : "--max-pods=58"

  // EKS cluster access key local variables
  ssh_key_name = var.CURRENT_ENVIRONMENT == "dev" ? "${var.common_info.project}-${var.CURRENT_ENVIRONMENT}-eks-key" : "${var.common_info.project}-eks-key"

  // S3 bucket with EKS cluster info local variables
  bucket_name = var.CURRENT_ENVIRONMENT == "dev" ? "${var.common_info.project}-${var.CURRENT_ENVIRONMENT}-eks" : "${var.common_info.project}-eks"

  // public subnets used in cluster
  subnets         = [
    data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-public-1a.id,
    data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-public-1b.id
  ]
  subnet_public_1a = data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-public-1a.id
  subnet_public_1b = data.terraform_remote_state.tfstate-network-resources.outputs.subnet_automation-public-1b.id

  // VPC id of VPC used in cluster
  vpc_id = data.terraform_remote_state.tfstate-network-resources.outputs.vpc_automation_id

  // default region used in AWS
  aws_default_region = "us-east-1"

  // TODO: After domain return to valid declare value as kre_record_hosted_zone_name = var.CURRENT_ENVIRONMENT == "dev" ? "kre-${var.CURRENT_ENVIRONMENT}.mettel-automation.net." : "kre.mettel-automation.net."
  kre_record_hosted_zone_name = var.CURRENT_ENVIRONMENT == "dev" ? "kre-test.mettel-automation.net." : "kre.mettel-automation.net."

  dnz_zone_email_tagger = var.CURRENT_ENVIRONMENT == "dev" ? "kre-email-tagger-dev.mettel-automation.net" : "kre-email-tagger.mettel-automation.net"
  dnz_zone_tnba         = var.CURRENT_ENVIRONMENT == "dev" ? "kre-tnba-dev.mettel-automation.net" : "kre-tnba.mettel-automation.net"
  dnz_zone_rta          = var.CURRENT_ENVIRONMENT == "dev" ? "kre-rta-dev.mettel-automation.net" : "kre-rta.mettel-automation.net"

}

 resource "null_resource" "associate-iam-oidc-provider" {

  provisioner "local-exec" {
    command = "eksctl utils associate-iam-oidc-provider --region us-east-1 --cluster ${local.cluster_name} --approve"
  }

  triggers = {
    always_run = timestamp()
  }

  depends_on = [
      //module.mettel-automation-eks-cluster,
      aws_iam_role.external-dns-role-eks
   ]
}

resource "null_resource" "update_kube_config" {
  provisioner "local-exec" {
    command = "aws eks update-kubeconfig --name ${local.cluster_name}"
  }

  triggers = {
    always_run = timestamp()
  }

  depends_on = [
      module.mettel-automation-eks-cluster,
   ]
}

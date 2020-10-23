/*resource "null_resource" "helm_release_nginx_ingress" {

  depends_on = [
      module.mettel-automation-eks-cluster,
      aws_s3_bucket_object.kubeconfig
  ]

  provisioner "local-exec" {
    command = "/bin/bash ${path.module}/scripts/helm_nginx_ingress.sh ${local.bucket_name} ${local.kubeconfig_dir}"
  }

  triggers = {
    always_run = timestamp()
  }
}*/

/*resource "null_resource" "configmap_aws_auth_installation" {

  depends_on = [
      # null_resource.update_record_elb_ingress,
      aws_s3_bucket_object.config_map_aws_auth
  ]

  provisioner "local-exec" {
    command = "/bin/bash ${path.module}/scripts/config_map_aws_auth_install.sh ${local.bucket_name} ${local.kubeconfig_dir}"
  }

  triggers = {
    always_run = timestamp()
  }
}*/

/*resource "null_resource" "update_record_elb_ingress" {

  depends_on = [null_resource.helm_release_nginx_ingress,
                aws_route53_zone.kre_hosted_zone]

  provisioner "local-exec" {
    command = "/bin/bash ${path.module}/scripts/update_route53_elb_alias.sh ${local.bucket_name} ${local.kubeconfig_dir} ${local.kre_record_alias_name} ${local.kre_record_hosted_zone_name} -u"
  }

  triggers = {
    always_run = timestamp()
  }
}*/

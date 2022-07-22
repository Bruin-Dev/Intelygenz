## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.1, < 1.2 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | = 3.70.0 |
| <a name="requirement_helm"></a> [helm](#requirement\_helm) | = 1.3.2 |
| <a name="requirement_kubernetes"></a> [kubernetes](#requirement\_kubernetes) | = 2.8.0 |
| <a name="requirement_local"></a> [local](#requirement\_local) | = 2.1.0 |
| <a name="requirement_null"></a> [null](#requirement\_null) | = 2.1.0 |
| <a name="requirement_template"></a> [template](#requirement\_template) | = 2.2.0 |
| <a name="requirement_tls"></a> [tls](#requirement\_tls) | = 3.1.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | 3.47.0 |
| <a name="provider_helm"></a> [helm](#provider\_helm) | 1.3.2 |
| <a name="provider_kubernetes"></a> [kubernetes](#provider\_kubernetes) | 2.0.1 |
| <a name="provider_null"></a> [null](#provider\_null) | 2.1.0 |
| <a name="provider_template"></a> [template](#provider\_template) | 2.1.0 |
| <a name="provider_tls"></a> [tls](#provider\_tls) | 2.2.0 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_mettel-automation-eks-cluster"></a> [mettel-automation-eks-cluster](#module\_mettel-automation-eks-cluster) | terraform-aws-modules/eks/aws | 17.1.0 |

## Resources

| Name | Type |
|------|------|
| [aws_cloudwatch_log_group.eks_log_group](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/cloudwatch_log_group) | resource |
| [aws_iam_policy.chartmuseum-eks](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/iam_policy) | resource |
| [aws_iam_policy.cluster-autoscaler-eks](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/iam_policy) | resource |
| [aws_iam_policy.external-dns-eks](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/iam_policy) | resource |
| [aws_iam_policy.external-secrets-eks](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/iam_policy) | resource |
| [aws_iam_policy.fluent-bit-eks](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/iam_policy) | resource |
| [aws_iam_role.chartmuseum-role-eks](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/iam_role) | resource |
| [aws_iam_role.cluster-autoscaler-role-eks](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/iam_role) | resource |
| [aws_iam_role.external-dns-role-eks](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/iam_role) | resource |
| [aws_iam_role.external-secrets-role-eks](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/iam_role) | resource |
| [aws_iam_role.fluent-bit-role-eks](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/iam_role) | resource |
| [aws_iam_role_policy_attachment.chartmuseum-eks-attachment](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.cluster-autoscaler-eks-attachment](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.external-dns-eks-attachment](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.external-secrets-eks-attachment](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.fluent-bit-eks-attachment](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/iam_role_policy_attachment) | resource |
| [aws_key_pair.aws_key_pair](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/key_pair) | resource |
| [aws_s3_bucket.bucket_chartmuseum](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/s3_bucket) | resource |
| [aws_s3_bucket_object.pem_file](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/s3_bucket_object) | resource |
| [aws_security_group.links_metrics_api_oreilly](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/security_group) | resource |
| [aws_security_group_rule.calls_from_ingress_elb_to_eks_worker_nodes](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/security_group_rule) | resource |
| [aws_ssm_parameter.external-secrets-eks-parameter](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ssm_parameter) | resource |
| [helm_release.chartmuseum](https://registry.terraform.io/providers/hashicorp/helm/1.3.2/docs/resources/release) | resource |
| [helm_release.cluster-autoscaler](https://registry.terraform.io/providers/hashicorp/helm/1.3.2/docs/resources/release) | resource |
| [helm_release.descheduler](https://registry.terraform.io/providers/hashicorp/helm/1.3.2/docs/resources/release) | resource |
| [helm_release.external-dns](https://registry.terraform.io/providers/hashicorp/helm/1.3.2/docs/resources/release) | resource |
| [helm_release.external-secrets](https://registry.terraform.io/providers/hashicorp/helm/1.3.2/docs/resources/release) | resource |
| [helm_release.ingress-nginx](https://registry.terraform.io/providers/hashicorp/helm/1.3.2/docs/resources/release) | resource |
| [helm_release.metrics-server](https://registry.terraform.io/providers/hashicorp/helm/1.3.2/docs/resources/release) | resource |
| [helm_release.reloader](https://registry.terraform.io/providers/hashicorp/helm/1.3.2/docs/resources/release) | resource |
| [kubernetes_namespace.prometheus](https://registry.terraform.io/providers/hashicorp/kubernetes/2.8.0/docs/resources/namespace) | resource |
| [kubernetes_secret.grafana_auth](https://registry.terraform.io/providers/hashicorp/kubernetes/2.8.0/docs/resources/secret) | resource |
| [null_resource.associate-iam-oidc-provider](https://registry.terraform.io/providers/hashicorp/null/2.1.0/docs/resources/resource) | resource |
| [null_resource.update_kube_config](https://registry.terraform.io/providers/hashicorp/null/2.1.0/docs/resources/resource) | resource |
| [tls_private_key.tls_private_key_eks](https://registry.terraform.io/providers/hashicorp/tls/3.1.0/docs/resources/private_key) | resource |
| [aws_acm_certificate.mettel_automation_certificate](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/data-sources/acm_certificate) | data source |
| [aws_caller_identity.current](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/data-sources/caller_identity) | data source |
| [aws_eks_cluster.cluster](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/data-sources/eks_cluster) | data source |
| [aws_eks_cluster_auth.cluster](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/data-sources/eks_cluster_auth) | data source |
| [aws_security_group.eks_nodes_security_group](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/data-sources/security_group) | data source |
| [aws_security_group.elb_ingress_nginx_eks_security_group](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/data-sources/security_group) | data source |
| [aws_subnet_ids.mettel-automation-private-subnets](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/data-sources/subnet_ids) | data source |
| [aws_vpc.mettel-automation-vpc](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/data-sources/vpc) | data source |
| [template_file.chartmuseum-eks-policy](https://registry.terraform.io/providers/hashicorp/template/2.2.0/docs/data-sources/file) | data source |
| [template_file.chartmuseum-eks-role](https://registry.terraform.io/providers/hashicorp/template/2.2.0/docs/data-sources/file) | data source |
| [template_file.cluster-autoscaler-eks-policy](https://registry.terraform.io/providers/hashicorp/template/2.2.0/docs/data-sources/file) | data source |
| [template_file.cluster-autoscaler-eks-role](https://registry.terraform.io/providers/hashicorp/template/2.2.0/docs/data-sources/file) | data source |
| [template_file.external-dns-eks-policy](https://registry.terraform.io/providers/hashicorp/template/2.2.0/docs/data-sources/file) | data source |
| [template_file.external-dns-eks-role](https://registry.terraform.io/providers/hashicorp/template/2.2.0/docs/data-sources/file) | data source |
| [template_file.external-secrets-eks-policy](https://registry.terraform.io/providers/hashicorp/template/2.2.0/docs/data-sources/file) | data source |
| [template_file.external-secrets-eks-role](https://registry.terraform.io/providers/hashicorp/template/2.2.0/docs/data-sources/file) | data source |
| [template_file.fluent-bit-eks-policy](https://registry.terraform.io/providers/hashicorp/template/2.2.0/docs/data-sources/file) | data source |
| [template_file.fluent-bit-eks-role](https://registry.terraform.io/providers/hashicorp/template/2.2.0/docs/data-sources/file) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_CHARTMUSEUM_HELM_CHART_VERSION"></a> [CHARTMUSEUM\_HELM\_CHART\_VERSION](#input\_CHARTMUSEUM\_HELM\_CHART\_VERSION) | Helm chart version used for chartmuseum | `string` | `"3.3.0"` | no |
| <a name="input_CHARTMUSEUM_PASSWORD"></a> [CHARTMUSEUM\_PASSWORD](#input\_CHARTMUSEUM\_PASSWORD) | Chartmuseum basic auth password | `string` | `""` | no |
| <a name="input_CHARTMUSEUM_USER"></a> [CHARTMUSEUM\_USER](#input\_CHARTMUSEUM\_USER) | Chartmuseum basic auth user | `string` | `""` | no |
| <a name="input_CLUSTER_AUTOSCALER_HELM_CHART_VERSION"></a> [CLUSTER\_AUTOSCALER\_HELM\_CHART\_VERSION](#input\_CLUSTER\_AUTOSCALER\_HELM\_CHART\_VERSION) | Helm chart version used for cluster-autoscaler | `string` | `"9.13.1"` | no |
| <a name="input_CURRENT_ENVIRONMENT"></a> [CURRENT\_ENVIRONMENT](#input\_CURRENT\_ENVIRONMENT) | Name of the environment to identify common resources to be used | `string` | `"dev"` | no |
| <a name="input_DESCHEDULER_HELM_CHART_VERSION"></a> [DESCHEDULER\_HELM\_CHART\_VERSION](#input\_DESCHEDULER\_HELM\_CHART\_VERSION) | Helm chart version used for descheduler | `string` | `"0.22.1"` | no |
| <a name="input_ENABLE_FLUENT_BIT"></a> [ENABLE\_FLUENT\_BIT](#input\_ENABLE\_FLUENT\_BIT) | If set to true, enable fluent-bit required components | `string` | `"false"` | no |
| <a name="input_EXTERNAL_DNS_HELM_CHART_VERSION"></a> [EXTERNAL\_DNS\_HELM\_CHART\_VERSION](#input\_EXTERNAL\_DNS\_HELM\_CHART\_VERSION) | Helm chart version used for external-dns | `string` | `"6.0.2"` | no |
| <a name="input_EXTERNAL_SECRETS_HELM_CHART_VERSION"></a> [EXTERNAL\_SECRETS\_HELM\_CHART\_VERSION](#input\_EXTERNAL\_SECRETS\_HELM\_CHART\_VERSION) | Helm chart version used for external-secrets | `string` | `"0.4.4"` | no |
| <a name="input_GRAFANA_ADMIN_PASSWORD"></a> [GRAFANA\_ADMIN\_PASSWORD](#input\_GRAFANA\_ADMIN\_PASSWORD) | Grafana admin password | `string` | `""` | no |
| <a name="input_GRAFANA_ADMIN_USER"></a> [GRAFANA\_ADMIN\_USER](#input\_GRAFANA\_ADMIN\_USER) | Grafana admin user | `string` | `""` | no |
| <a name="input_INGRESS_NGINX_HELM_CHART_VERSION"></a> [INGRESS\_NGINX\_HELM\_CHART\_VERSION](#input\_INGRESS\_NGINX\_HELM\_CHART\_VERSION) | Helm chart version used for ingress-nginx | `string` | `"4.0.13"` | no |
| <a name="input_METRICS_SERVER_HELM_CHART_VERSION"></a> [METRICS\_SERVER\_HELM\_CHART\_VERSION](#input\_METRICS\_SERVER\_HELM\_CHART\_VERSION) | Helm chart version used for  metrics-server | `string` | `"3.8.2"` | no |
| <a name="input_RELOADER_HELM_CHART_VERSION"></a> [RELOADER\_HELM\_CHART\_VERSION](#input\_RELOADER\_HELM\_CHART\_VERSION) | Helm chart version used for reloader | `string` | `"0.0.103"` | no |
| <a name="input_WHITELISTED_IPS"></a> [WHITELISTED\_IPS](#input\_WHITELISTED\_IPS) | Allowed IPs to access Load Balancer created by nginx ingress controller | `list(string)` | <pre>[<br>  ""<br>]</pre> | no |
| <a name="input_WHITELISTED_IPS_OREILLY"></a> [WHITELISTED\_IPS\_OREILLY](#input\_WHITELISTED\_IPS\_OREILLY) | Allowed IPs to access Load Balancer created for oreilly client | `list(string)` | <pre>[<br>  ""<br>]</pre> | no |
| <a name="input_common_info"></a> [common\_info](#input\_common\_info) | Global Tags # mettel-automation project | `map(string)` | <pre>{<br>  "project": "mettel-automation",<br>  "provisioning": "Terraform"<br>}</pre> | no |
| <a name="input_map_users"></a> [map\_users](#input\_map\_users) | Additional IAM users to add to the aws-auth configmap. | <pre>list(object({<br>    userarn  = string<br>    username = string<br>    groups   = list(string)<br>  }))</pre> | <pre>[<br>  {<br>    "groups": [<br>      "system:masters"<br>    ],<br>    "userarn": "arn:aws:iam::374050862540:user/angel.costales",<br>    "username": "angel.costales"<br>  }<br>]</pre> | no |
| <a name="input_worker_node_instance_type"></a> [worker\_node\_instance\_type](#input\_worker\_node\_instance\_type) | n/a | `map(string)` | <pre>{<br>  "dev": "m6a.large",<br>  "production": "m6a.large"<br>}</pre> | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_fluent-bit-log-group-name"></a> [fluent-bit-log-group-name](#output\_fluent-bit-log-group-name) | n/a |
| <a name="output_fluent-bit-role-arn"></a> [fluent-bit-role-arn](#output\_fluent-bit-role-arn) | n/a |
| <a name="output_oreilly-security-group-id"></a> [oreilly-security-group-id](#output\_oreilly-security-group-id) | Oreilly whitelisted security group access |

## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.1, < 1.2 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | = 4.6.0 |
| <a name="requirement_helm"></a> [helm](#requirement\_helm) | = 2.4.1 |
| <a name="requirement_http"></a> [http](#requirement\_http) | 2.4.1 |
| <a name="requirement_kubectl"></a> [kubectl](#requirement\_kubectl) | >=1.13.1 |
| <a name="requirement_kubernetes"></a> [kubernetes](#requirement\_kubernetes) | = 2.9.0 |
| <a name="requirement_local"></a> [local](#requirement\_local) | = 2.2.2 |
| <a name="requirement_null"></a> [null](#requirement\_null) | = 3.1.1 |
| <a name="requirement_template"></a> [template](#requirement\_template) | = 2.2.0 |
| <a name="requirement_tls"></a> [tls](#requirement\_tls) | = 3.1.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | = 4.6.0 |
| <a name="provider_helm"></a> [helm](#provider\_helm) | = 2.4.1 |
| <a name="provider_http"></a> [http](#provider\_http) | 2.4.1 |
| <a name="provider_kubectl"></a> [kubectl](#provider\_kubectl) | >=1.13.1 |
| <a name="provider_kubernetes"></a> [kubernetes](#provider\_kubernetes) | = 2.9.0 |
| <a name="provider_template"></a> [template](#provider\_template) | = 2.2.0 |
| <a name="provider_terraform"></a> [terraform](#provider\_terraform) | n/a |
| <a name="provider_tls"></a> [tls](#provider\_tls) | = 3.1.0 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_cert_manager"></a> [cert\_manager](#module\_cert\_manager) | terraform-iaac/cert-manager/kubernetes | n/a |
| <a name="module_mettel-automation-eks-cluster"></a> [mettel-automation-eks-cluster](#module\_mettel-automation-eks-cluster) | terraform-aws-modules/eks/aws | 18.11.0 |
| <a name="module_vpc_cni_irsa"></a> [vpc\_cni\_irsa](#module\_vpc\_cni\_irsa) | terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks | n/a |

## Resources

| Name | Type |
|------|------|
| [aws_eks_addon.coredns](https://registry.terraform.io/providers/hashicorp/aws/4.6.0/docs/resources/eks_addon) | resource |
| [aws_eks_addon.kube_proxy](https://registry.terraform.io/providers/hashicorp/aws/4.6.0/docs/resources/eks_addon) | resource |
| [aws_eks_addon.vpc_cni](https://registry.terraform.io/providers/hashicorp/aws/4.6.0/docs/resources/eks_addon) | resource |
| [aws_iam_policy.aws-ebs-csi-driver-eks](https://registry.terraform.io/providers/hashicorp/aws/4.6.0/docs/resources/iam_policy) | resource |
| [aws_iam_policy.cert-manager-eks](https://registry.terraform.io/providers/hashicorp/aws/4.6.0/docs/resources/iam_policy) | resource |
| [aws_iam_policy.external-dns-eks](https://registry.terraform.io/providers/hashicorp/aws/4.6.0/docs/resources/iam_policy) | resource |
| [aws_iam_role.aws-ebs-csi-driver-role-eks](https://registry.terraform.io/providers/hashicorp/aws/4.6.0/docs/resources/iam_role) | resource |
| [aws_iam_role.cert-manager-role-eks](https://registry.terraform.io/providers/hashicorp/aws/4.6.0/docs/resources/iam_role) | resource |
| [aws_iam_role.external-dns-role-eks](https://registry.terraform.io/providers/hashicorp/aws/4.6.0/docs/resources/iam_role) | resource |
| [aws_iam_role_policy_attachment.aws-ebs-csi-driver-eks-attachment](https://registry.terraform.io/providers/hashicorp/aws/4.6.0/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.cert-manager-eks-attachment](https://registry.terraform.io/providers/hashicorp/aws/4.6.0/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.external-dns-eks-attachment](https://registry.terraform.io/providers/hashicorp/aws/4.6.0/docs/resources/iam_role_policy_attachment) | resource |
| [aws_key_pair.aws_key_pair](https://registry.terraform.io/providers/hashicorp/aws/4.6.0/docs/resources/key_pair) | resource |
| [aws_kms_key.kms_key](https://registry.terraform.io/providers/hashicorp/aws/4.6.0/docs/resources/kms_key) | resource |
| [aws_s3_object.pem_file](https://registry.terraform.io/providers/hashicorp/aws/4.6.0/docs/resources/s3_object) | resource |
| [helm_release.aws-ebs-csi-driver](https://registry.terraform.io/providers/hashicorp/helm/2.4.1/docs/resources/release) | resource |
| [helm_release.descheduler](https://registry.terraform.io/providers/hashicorp/helm/2.4.1/docs/resources/release) | resource |
| [helm_release.external-dns](https://registry.terraform.io/providers/hashicorp/helm/2.4.1/docs/resources/release) | resource |
| [helm_release.ingress-nginx](https://registry.terraform.io/providers/hashicorp/helm/2.4.1/docs/resources/release) | resource |
| [helm_release.metrics-server](https://registry.terraform.io/providers/hashicorp/helm/2.4.1/docs/resources/release) | resource |
| [kubectl_manifest.aws_auth](https://registry.terraform.io/providers/gavinbunney/kubectl/latest/docs/resources/manifest) | resource |
| [kubernetes_storage_class.gp3](https://registry.terraform.io/providers/hashicorp/kubernetes/2.9.0/docs/resources/storage_class) | resource |
| [tls_private_key.tls_private_key_eks](https://registry.terraform.io/providers/hashicorp/tls/3.1.0/docs/resources/private_key) | resource |
| [aws_ami.eks_worker_ami_name_filter](https://registry.terraform.io/providers/hashicorp/aws/4.6.0/docs/data-sources/ami) | data source |
| [aws_caller_identity.current](https://registry.terraform.io/providers/hashicorp/aws/4.6.0/docs/data-sources/caller_identity) | data source |
| [aws_eks_cluster.cluster](https://registry.terraform.io/providers/hashicorp/aws/4.6.0/docs/data-sources/eks_cluster) | data source |
| [aws_eks_cluster_auth.cluster](https://registry.terraform.io/providers/hashicorp/aws/4.6.0/docs/data-sources/eks_cluster_auth) | data source |
| [aws_iam_policy_document.kms](https://registry.terraform.io/providers/hashicorp/aws/4.6.0/docs/data-sources/iam_policy_document) | data source |
| [aws_route53_zone.mettel_automation](https://registry.terraform.io/providers/hashicorp/aws/4.6.0/docs/data-sources/route53_zone) | data source |
| [http_http.wait_for_cluster](https://registry.terraform.io/providers/terraform-aws-modules/http/2.4.1/docs/data-sources/http) | data source |
| [template_file.aws-ebs-csi-driver-eks-policy](https://registry.terraform.io/providers/hashicorp/template/2.2.0/docs/data-sources/file) | data source |
| [template_file.aws-ebs-csi-driver-eks-role](https://registry.terraform.io/providers/hashicorp/template/2.2.0/docs/data-sources/file) | data source |
| [template_file.cert-manager-eks-policy](https://registry.terraform.io/providers/hashicorp/template/2.2.0/docs/data-sources/file) | data source |
| [template_file.cert-manager-eks-role](https://registry.terraform.io/providers/hashicorp/template/2.2.0/docs/data-sources/file) | data source |
| [template_file.external-dns-eks-policy](https://registry.terraform.io/providers/hashicorp/template/2.2.0/docs/data-sources/file) | data source |
| [template_file.external-dns-eks-role](https://registry.terraform.io/providers/hashicorp/template/2.2.0/docs/data-sources/file) | data source |
| [terraform_remote_state.tfstate-network-resources](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |
| [terraform_remote_state.tfstate-s3-bucket-eks](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_AWS_SECRET_ACCESS_KEY"></a> [AWS\_SECRET\_ACCESS\_KEY](#input\_AWS\_SECRET\_ACCESS\_KEY) | AWS Secret Access Key credentials | `string` | `""` | no |
| <a name="input_CURRENT_ENVIRONMENT"></a> [CURRENT\_ENVIRONMENT](#input\_CURRENT\_ENVIRONMENT) | Name of the environment to identify common resources to be used | `string` | `"dev"` | no |
| <a name="input_DESCHEDULER_HELM_CHART_VERSION"></a> [DESCHEDULER\_HELM\_CHART\_VERSION](#input\_DESCHEDULER\_HELM\_CHART\_VERSION) | Helm chart version used for descheduler | `string` | `"0.23.2"` | no |
| <a name="input_EBS_CSI_HELM_CHART_VERSION"></a> [EBS\_CSI\_HELM\_CHART\_VERSION](#input\_EBS\_CSI\_HELM\_CHART\_VERSION) | Helm chart version used for aws-ebs-csi-driver | `string` | `"2.6.4"` | no |
| <a name="input_EKS_ADDON_COREDNS_VERSION"></a> [EKS\_ADDON\_COREDNS\_VERSION](#input\_EKS\_ADDON\_COREDNS\_VERSION) | EKS addon version used for COREDNS | `string` | `"v1.8.4-eksbuild.1"` | no |
| <a name="input_EKS_ADDON_EBS_CSI_VERSION"></a> [EKS\_ADDON\_EBS\_CSI\_VERSION](#input\_EKS\_ADDON\_EBS\_CSI\_VERSION) | EKS addon version used for EBS CSI | `string` | `"v1.4.0-eksbuild.preview"` | no |
| <a name="input_EKS_ADDON_KUBE_PROXY_VERSION"></a> [EKS\_ADDON\_KUBE\_PROXY\_VERSION](#input\_EKS\_ADDON\_KUBE\_PROXY\_VERSION) | EKS addon version used for KUBE-PROXY | `string` | `"v1.21.2-eksbuild.2"` | no |
| <a name="input_EKS_ADDON_VPC_CNI_VERSION"></a> [EKS\_ADDON\_VPC\_CNI\_VERSION](#input\_EKS\_ADDON\_VPC\_CNI\_VERSION) | EKS addon version used for VPC CNI | `string` | `"v1.10.2-eksbuild.1"` | no |
| <a name="input_EKS_CLUSTER_ADMIN_IAM_USER_NAME"></a> [EKS\_CLUSTER\_ADMIN\_IAM\_USER\_NAME](#input\_EKS\_CLUSTER\_ADMIN\_IAM\_USER\_NAME) | IAM user name to admin cluster | `string` | `"angel.costales"` | no |
| <a name="input_EXTERNAL_DNS_HELM_CHART_VERSION"></a> [EXTERNAL\_DNS\_HELM\_CHART\_VERSION](#input\_EXTERNAL\_DNS\_HELM\_CHART\_VERSION) | Helm chart version used for external-dns | `string` | `"6.2.1"` | no |
| <a name="input_INGRESS_NGINX_HELM_CHART_VERSION"></a> [INGRESS\_NGINX\_HELM\_CHART\_VERSION](#input\_INGRESS\_NGINX\_HELM\_CHART\_VERSION) | Helm chart version used for ingress-nginx | `string` | `"4.0.13"` | no |
| <a name="input_METRICS_SERVER_HELM_CHART_VERSION"></a> [METRICS\_SERVER\_HELM\_CHART\_VERSION](#input\_METRICS\_SERVER\_HELM\_CHART\_VERSION) | Helm chart version used for metrics-server | `string` | `"3.8.2"` | no |
| <a name="input_WHITELISTED_IPS"></a> [WHITELISTED\_IPS](#input\_WHITELISTED\_IPS) | Allowed IPs to access Load Balancer created by nginx ingress controller | `list(string)` | <pre>[<br>  ""<br>]</pre> | no |
| <a name="input_common_info"></a> [common\_info](#input\_common\_info) | Global Tags # kre infrastructure for mettel-automation project | `map(string)` | <pre>{<br>  "project": "mettel-automation-kre",<br>  "provisioning": "Terraform"<br>}</pre> | no |

## Outputs

No outputs.

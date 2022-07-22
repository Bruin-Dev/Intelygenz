## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.1, < 1.2 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | = 3.70.0 |
| <a name="requirement_template"></a> [template](#requirement\_template) | = 2.2.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | 3.47.0 |
| <a name="provider_template"></a> [template](#provider\_template) | 2.1.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [aws_acm_certificate.ssl_certificate](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/acm_certificate) | resource |
| [aws_acm_certificate_validation.cert_validation_ssl_certificate](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/acm_certificate_validation) | resource |
| [aws_iam_policy.assume-developer-role](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/iam_policy) | resource |
| [aws_iam_policy.assume-devops-role](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/iam_policy) | resource |
| [aws_iam_policy.assume-ops-role](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/iam_policy) | resource |
| [aws_iam_role.developer_eks](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/iam_role) | resource |
| [aws_iam_role.devops_eks](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/iam_role) | resource |
| [aws_iam_role.ops_eks](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/iam_role) | resource |
| [aws_iam_role_policy.developer-role-policy-permissions](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/iam_role_policy) | resource |
| [aws_iam_role_policy.devops-role-policy-permissions](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/iam_role_policy) | resource |
| [aws_iam_role_policy.ops-role-policy-permissions](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/iam_role_policy) | resource |
| [aws_iam_user_policy_attachment.attach-developer-user](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/iam_user_policy_attachment) | resource |
| [aws_iam_user_policy_attachment.attach-devops-user](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/iam_user_policy_attachment) | resource |
| [aws_iam_user_policy_attachment.attach-ops-user](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/iam_user_policy_attachment) | resource |
| [aws_route53_record.ssl_certificate_dns_validation](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/route53_record) | resource |
| [aws_caller_identity.current](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/data-sources/caller_identity) | data source |
| [aws_iam_user.igz_developer_users](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/data-sources/iam_user) | data source |
| [aws_iam_user.igz_devops_users](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/data-sources/iam_user) | data source |
| [aws_iam_user.igz_ops_users](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/data-sources/iam_user) | data source |
| [aws_route53_zone.mettel_automation](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/data-sources/route53_zone) | data source |
| [template_file.assume-developer-role](https://registry.terraform.io/providers/hashicorp/template/2.2.0/docs/data-sources/file) | data source |
| [template_file.assume-devops-role](https://registry.terraform.io/providers/hashicorp/template/2.2.0/docs/data-sources/file) | data source |
| [template_file.assume-ops-role](https://registry.terraform.io/providers/hashicorp/template/2.2.0/docs/data-sources/file) | data source |
| [template_file.developer-role-policy](https://registry.terraform.io/providers/hashicorp/template/2.2.0/docs/data-sources/file) | data source |
| [template_file.developer_eks_role](https://registry.terraform.io/providers/hashicorp/template/2.2.0/docs/data-sources/file) | data source |
| [template_file.devops-role-policy](https://registry.terraform.io/providers/hashicorp/template/2.2.0/docs/data-sources/file) | data source |
| [template_file.devops_eks_role](https://registry.terraform.io/providers/hashicorp/template/2.2.0/docs/data-sources/file) | data source |
| [template_file.ops-role-policy](https://registry.terraform.io/providers/hashicorp/template/2.2.0/docs/data-sources/file) | data source |
| [template_file.ops_eks_role](https://registry.terraform.io/providers/hashicorp/template/2.2.0/docs/data-sources/file) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_CURRENT_ENVIRONMENT"></a> [CURRENT\_ENVIRONMENT](#input\_CURRENT\_ENVIRONMENT) | Name of the environment to identify common resources to be used | `string` | `"dev"` | no |
| <a name="input_EKS_CLUSTER_NAME"></a> [EKS\_CLUSTER\_NAME](#input\_EKS\_CLUSTER\_NAME) | EKS Cluster name to obtain data | `string` | `""` | no |
| <a name="input_common_info"></a> [common\_info](#input\_common\_info) | Global Tags # mettel-automation project | `map(string)` | <pre>{<br>  "project": "mettel-automation",<br>  "provisioning": "Terraform"<br>}</pre> | no |
| <a name="input_eks_developer_users"></a> [eks\_developer\_users](#input\_eks\_developer\_users) | List of users with developer role access in EKS cluster | `list(string)` | <pre>[<br>  "some.user",<br>  "foo.var"<br>]</pre> | no |
| <a name="input_eks_devops_users"></a> [eks\_devops\_users](#input\_eks\_devops\_users) | List of users with devops role access in EKS cluster | `list(string)` | <pre>[<br>  "foo.vartwo"<br>]</pre> | no |
| <a name="input_eks_ops_users"></a> [eks\_ops\_users](#input\_eks\_ops\_users) | List of users with ops role access in EKS cluster | `list(string)` | <pre>[<br>  "jon.du"<br>]</pre> | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_eks_developer_roles"></a> [eks\_developer\_roles](#output\_eks\_developer\_roles) | List of developer users roles |
| <a name="output_eks_devops_roles"></a> [eks\_devops\_roles](#output\_eks\_devops\_roles) | List of devops users roles |
| <a name="output_ssl-certificate-arn"></a> [ssl-certificate-arn](#output\_ssl-certificate-arn) | AWS SSL certificate for automation-engine.net |

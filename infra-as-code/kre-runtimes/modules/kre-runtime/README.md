## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.1, < 1.2 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | = 3.70.0 |
| <a name="requirement_local"></a> [local](#requirement\_local) | = 2.1.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | = 3.70.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [aws_route53_record.kre_ns](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/route53_record) | resource |
| [aws_route53_zone.kre_hosted_zone](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/route53_zone) | resource |
| [aws_eks_cluster.cluster](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/data-sources/eks_cluster) | data source |
| [aws_eks_cluster_auth.cluster](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/data-sources/eks_cluster_auth) | data source |
| [aws_route53_zone.mettel_automation](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/data-sources/route53_zone) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_CURRENT_ENVIRONMENT"></a> [CURRENT\_ENVIRONMENT](#input\_CURRENT\_ENVIRONMENT) | Name of the environment to identify common resources to be used | `string` | `"dev"` | no |
| <a name="input_HOSTED_ZONE_DOMAIN_NAME"></a> [HOSTED\_ZONE\_DOMAIN\_NAME](#input\_HOSTED\_ZONE\_DOMAIN\_NAME) | Name of the commmon domain name used in the project | `string` | `"mettel-automation.net"` | no |
| <a name="input_RUNTIME_NAME"></a> [RUNTIME\_NAME](#input\_RUNTIME\_NAME) | Name of the runtime to create in KRE | `string` | `""` | no |
| <a name="input_common_info"></a> [common\_info](#input\_common\_info) | Global Tags # kre infrastructure for mettel-automation project | `map(string)` | <pre>{<br>  "project": "mettel-automation-kre",<br>  "provisioning": "Terraform"<br>}</pre> | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_kre_runtime_hosted_zone_id"></a> [kre\_runtime\_hosted\_zone\_id](#output\_kre\_runtime\_hosted\_zone\_id) | n/a |

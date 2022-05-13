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

| Name | Source | Version |
|------|--------|---------|
| <a name="module_ses_domain"></a> [ses\_domain](#module\_ses\_domain) | trussworks/ses-domain/aws | 3.2.0 |

## Resources

| Name | Type |
|------|------|
| [aws_route53_record.temp_domain_ns_records](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/route53_record) | resource |
| [aws_route53_record.temp_spf](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/route53_record) | resource |
| [aws_route53_zone.temp_domain](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/route53_zone) | resource |
| [aws_s3_bucket.temp_bucket](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/s3_bucket) | resource |
| [aws_s3_bucket_public_access_block.public_access_block](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/s3_bucket_public_access_block) | resource |
| [aws_ses_active_receipt_rule_set.main](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ses_active_receipt_rule_set) | resource |
| [aws_ses_email_identity.email_identities](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ses_email_identity) | resource |
| [aws_ses_receipt_rule_set.main](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ses_receipt_rule_set) | resource |
| [aws_caller_identity.current](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/data-sources/caller_identity) | data source |
| [aws_iam_account_alias.current](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/data-sources/iam_account_alias) | data source |
| [aws_iam_policy_document.s3_allow_ses_puts](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/data-sources/iam_policy_document) | data source |
| [aws_partition.current](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/data-sources/partition) | data source |
| [aws_route53_zone.mettel_automation](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/data-sources/route53_zone) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_AWS_SECRET_ACCESS_KEY"></a> [AWS\_SECRET\_ACCESS\_KEY](#input\_AWS\_SECRET\_ACCESS\_KEY) | AWS Secret Access Key credentials | `string` | `""` | no |
| <a name="input_CURRENT_ENVIRONMENT"></a> [CURRENT\_ENVIRONMENT](#input\_CURRENT\_ENVIRONMENT) | Name of the environment to identify common resources to be used | `string` | `"dev"` | no |
| <a name="input_common_info"></a> [common\_info](#input\_common\_info) | Global Tags # kre infrastructure for mettel-automation project | `map(string)` | <pre>{<br>  "project": "mettel-automation-kre",<br>  "provisioning": "Terraform"<br>}</pre> | no |
| <a name="input_enable_spf_record"></a> [enable\_spf\_record](#input\_enable\_spf\_record) | n/a | `bool` | `true` | no |
| <a name="input_extra_ses_records"></a> [extra\_ses\_records](#input\_extra\_ses\_records) | n/a | `list(string)` | `[]` | no |
| <a name="input_igz_users_email"></a> [igz\_users\_email](#input\_igz\_users\_email) | IGZ user for create email accounts | `list` | <pre>[<br>  "alberto.iglesias@intelygenz.com",<br>  "angel.costales@intelygenz.com",<br>  "angel.sanchez@intelygenz.com",<br>  "angelluis.piquero@intelygenz.com",<br>  "brandon.samudio@intelygenz.com",<br>  "daniel.fernandez@intelygenz.com",<br>  "gustavo.marin@intelygenz.com",<br>  "jonas.dacruz@intelygenz.com",<br>  "joseluis.vega@intelygenz.com",<br>  "alejandro.aceituna@intelygenz.com",<br>  "julia.hossu@intelygenz.com",<br>  "mettel@intelygenz.com",<br>  "marc.vivancos@intelygenz.com"<br>]</pre> | no |
| <a name="input_region"></a> [region](#input\_region) | n/a | `string` | `"us-east-1"` | no |
| <a name="input_subdomain_name_prefix"></a> [subdomain\_name\_prefix](#input\_subdomain\_name\_prefix) | n/a | `string` | `"intelygenz"` | no |

## Outputs

No outputs.

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
| [aws_s3_bucket.bucket](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/s3_bucket) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_AWS_SECRET_ACCESS_KEY"></a> [AWS\_SECRET\_ACCESS\_KEY](#input\_AWS\_SECRET\_ACCESS\_KEY) | AWS Secret Access Key credentials | `string` | `""` | no |
| <a name="input_CURRENT_ENVIRONMENT"></a> [CURRENT\_ENVIRONMENT](#input\_CURRENT\_ENVIRONMENT) | Name of the environment to identify common resources to be used | `string` | `"dev"` | no |
| <a name="input_common_info"></a> [common\_info](#input\_common\_info) | Global Tags # kre infrastructure for mettel-automation project | `map(string)` | <pre>{<br>  "project": "mettel-automation-kre",<br>  "provisioning": "Terraform"<br>}</pre> | no |

## Outputs

No outputs.

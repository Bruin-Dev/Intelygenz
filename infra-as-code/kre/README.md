## Requirements

| Name | Version |
|------|---------|
| terraform | = 0.14.4 |
| aws | =3.4.0 |
| external | = 1.2.0 |
| helm | = 1.3.2 |
| kubernetes | = 2.0.1 |
| local | = 1.4.0 |
| null | = 2.1.0 |
| random | = 2.3.0 |
| template | = 2.1.0 |
| tls | = 2.2.0 |

## Providers

No provider.

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| AWS\_SECRET\_ACCESS\_KEY | AWS Secret Access Key credentials | `string` | `""` | no |
| CURRENT\_ENVIRONMENT | Name of the environment to identify common resources to be used | `string` | `"dev"` | no |
| common\_info | Global Tags # kre infrastructure for mettel-automation project | `map(string)` | <pre>{<br>  "project": "mettel-automation-kre",<br>  "provisioning": "Terraform"<br>}</pre> | no |

## Outputs

No output.


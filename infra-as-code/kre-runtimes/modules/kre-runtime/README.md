## Requirements

| Name | Version |
|------|---------|
| terraform | = 0.14.4 |
| aws | =3.4.0 |
| external | = 1.2.0 |
| local | = 1.4.0 |
| null | = 2.1.0 |
| random | = 2.3.0 |
| template | = 2.1.0 |
| tls | = 2.2.0 |

## Providers

| Name | Version |
|------|---------|
| aws | =3.4.0 |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| CURRENT\_ENVIRONMENT | Name of the environment to identify common resources to be used | `string` | `"dev"` | no |
| HOSTED\_ZONE\_DOMAIN\_NAME | Name of the commmon domain name used in the project | `string` | `"mettel-automation.net"` | no |
| RUNTIME\_NAME | Name of the runtime to create in KRE | `string` | `""` | no |
| common\_info | Global Tags # kre infrastructure for mettel-automation project | `map(string)` | <pre>{<br>  "project": "mettel-automation-kre",<br>  "provisioning": "Terraform"<br>}</pre> | no |

## Outputs

| Name | Description |
|------|-------------|
| kre\_runtime\_hosted\_zone\_id | n/a |


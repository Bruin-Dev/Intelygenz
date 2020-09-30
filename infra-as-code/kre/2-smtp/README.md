## Requirements

| Name | Version |
|------|---------|
| terraform | >= 0.12,<=0.13.1 |
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
| common\_info | Global Tags # mettel-automation project | `map(string)` | <pre>{<br>  "project": "mettel-automation-kre",<br>  "provisioning": "Terraform"<br>}</pre> | no |
| enable\_spf\_record | n/a | `bool` | `true` | no |
| extra\_ses\_records | n/a | `list(string)` | `[]` | no |
| igz\_users\_email | IGZ user for create email accounts | `list` | <pre>[<br>  "mettel@intelygenz.com",<br>  "francisco.capllonch@intelygenz.com",<br>  "xoan.mallon@intelygenz.com"<br>]</pre> | no |
| region | n/a | `string` | `"us-east-1"` | no |
| subdomain\_name\_prefix | n/a | `string` | `"intelygenz"` | no |

## Outputs

No output.


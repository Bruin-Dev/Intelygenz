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

| Name | Version |
|------|---------|
| aws | =3.4.0 |
| template | = 2.1.0 |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| AWS\_SECRET\_ACCESS\_KEY | AWS Secret Access Key credentials | `string` | `""` | no |
| CURRENT\_ENVIRONMENT | Name of the environment to identify common resources to be used | `string` | `"dev"` | no |
| common\_info | Global Tags # kre infrastructure for mettel-automation project | `map(string)` | <pre>{<br>  "project": "mettel-automation-kre",<br>  "provisioning": "Terraform"<br>}</pre> | no |
| eks\_developer\_users | List of users with developer role access in EKS cluster | `list(string)` | <pre>[<br>  "brandon.samudio",<br>  "daniel.fernandez",<br>  "joseluis.vega",<br>  "marc.vivancos"<br>]</pre> | no |
| eks\_devops\_users | List of users with devops role access in EKS cluster | `list(string)` | <pre>[<br>  "alberto.iglesias",<br>  "angel.costales",<br>  "angel.luis.piquero",<br>  "xisco.capllonch",<br>  "xoan.mallon.devops"<br>]</pre> | no |

## Outputs

| Name | Description |
|------|-------------|
| eks\_developer\_roles | List of developer users roles |
| eks\_devops\_roles | List of devops users roles |


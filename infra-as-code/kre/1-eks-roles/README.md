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
| template | = 2.1.0 |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| CURRENT\_ENVIRONMENT | Name of the environment to identify common resources to be used | `string` | `"dev"` | no |
| common\_info | Global Tags # kre infrastructure for mettel-automation project | `map(string)` | <pre>{<br>  "project": "mettel-automation-kre",<br>  "provisioning": "Terraform"<br>}</pre> | no |
| eks\_developer\_ops\_privileged\_users | List of users with developer-ops-privileged role access in EKS cluster | `list(string)` | <pre>[<br>  "xisco.capllonch",<br>  "xoan.mallon.developer"<br>]</pre> | no |
| eks\_developer\_users | List of users with developer role access in EKS cluster | `list(string)` | <pre>[<br>  "brandon.samudio",<br>  "daniel.fernandez",<br>  "joseluis.vega",<br>  "sancho.munoz"<br>]</pre> | no |
| eks\_devops\_users | List of users with devops role access in EKS cluster | `list(string)` | <pre>[<br>  "alberto.iglesias",<br>  "angel.costales",<br>  "angel.luis.piquero",<br>  "xoan.mallon.devops"<br>]</pre> | no |

## Outputs

| Name | Description |
|------|-------------|
| eks\_developer\_ops\_privileged\_roles | List of developer-ops-privileged users roles |
| eks\_developer\_roles | List of developer users roles |
| eks\_devops\_roles | List of devops users roles |


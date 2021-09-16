## Requirements

| Name | Version |
|------|---------|
| terraform | = 0.14.4 |
| aws | = 3.26.0 |
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
| aws | = 3.26.0 |
| template | = 2.1.0 |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| CURRENT\_ENVIRONMENT | Name of the environment to identify common resources to be used | `string` | `"dev"` | no |
| EKS\_CLUSTER\_NAME | EKS Cluster name to obtain data | `string` | `""` | no |
| common\_info | Global Tags # mettel-automation project | `map(string)` | <pre>{<br>  "project": "mettel-automation",<br>  "provisioning": "Terraform"<br>}</pre> | no |
| eks\_developer\_users | n/a | `list(string)` | <pre>[<br>  "brandon.samudio",<br>  "daniel.fernandez",<br>  "joseluis.vega",<br>  "marc.vivancos",<br>  "xoan.mallon.developer"<br>]</pre> | no |
| eks\_devops\_users | List of users with devops role access in EKS cluster | `list(string)` | <pre>[<br>  "alberto.iglesias",<br>  "angel.luis.piquero",<br>  "xoan.mallon"<br>]</pre> | no |

## Outputs

| Name | Description |
|------|-------------|
| eks\_developer\_roles | List of developer users roles |
| eks\_devops\_roles | List of devops users roles |


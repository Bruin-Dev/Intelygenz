## Requirements

| Name | Version |
|------|---------|
| aws | =2.49.0 |

## Providers

| Name | Version |
|------|---------|
| aws | =2.49.0 |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| CURRENT\_ENVIRONMENT | Name of the environment to identify the network resources to be used | `string` | `"dev"` | no |
| EKS\_CLUSTER\_NAMES | Name of the EKS cluster to allow deploy its ELB in the public subnets | `map` | <pre>{<br>  "dev": [<br>    "mettel-automation-kre-dev",<br>    "mettel-automation-dev"<br>  ],<br>  "production": [<br>    "mettel-automation-kre",<br>    "mettel-automation"<br>  ]<br>}</pre> | no |
| EKS\_KRE\_BASE\_NAME | Base name used for EKS cluster used to deploy kre component | `string` | `"mettel-automation-kre"` | no |
| EKS\_PROJECT\_BASE\_NAME | Base name used for EKS cluster used to deploy project components | `string` | `"mettel-automation"` | no |
| cdir\_private\_1 | CIDR base for private subnet 1 | `map` | <pre>{<br>  "dev": "10.2.11.0/24",<br>  "production": "10.1.11.0/24"<br>}</pre> | no |
| cdir\_private\_2 | CIDR base for private subnet 2 | `map` | <pre>{<br>  "dev": "10.2.12.0/24",<br>  "production": "10.1.12.0/24"<br>}</pre> | no |
| cdir\_public\_1 | CIDR base for public subnet 1 | `map` | <pre>{<br>  "dev": "10.2.1.0/24",<br>  "production": "10.1.1.0/24"<br>}</pre> | no |
| cdir\_public\_2 | CIDR base for public subnet 2 | `map` | <pre>{<br>  "dev": "10.2.2.0/24",<br>  "production": "10.1.2.0/24"<br>}</pre> | no |
| cidr\_base | CIDR base for the environment | `map` | <pre>{<br>  "dev": "10.2.0.0/16",<br>  "production": "10.1.0.0/16"<br>}</pre> | no |

## Outputs

| Name | Description |
|------|-------------|
| subnet\_automation-private-1a | n/a |
| subnet\_automation-private-1b | n/a |
| subnet\_automation-public-1a | n/a |
| subnet\_automation-public-1b | n/a |
| vpc\_automation\_id | n/a |


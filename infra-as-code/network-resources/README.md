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
| CURRENT\_ENVIRONMENT | Name of the environment to identify common resources to be used | `string` | `"dev"` | no |
| EKS\_CLUSTER\_NAMES | Name of the EKS cluster to allow deploy its ELB in the public subnets | `map` | <pre>{<br>  "dev": [<br>    "mettel-automation-kre-dev",<br>    "mettel-automation-dev"<br>  ],<br>  "production": [<br>    "mettel-automation-kre",<br>    "mettel-automation"<br>  ]<br>}</pre> | no |
| EKS\_KRE\_BASE\_NAME | Base name used for EKS cluster used to deploy kre component | `string` | `"mettel-automation-kre"` | no |
| EKS\_PROJECT\_BASE\_NAME | Base name used for EKS cluster used to deploy project components | `string` | `"mettel-automation"` | no |
| cdir\_private\_1 | CIDR base for private subnet 1 | `map` | <pre>{<br>  "dev": "172.31.86.0/24",<br>  "production": "172.31.90.0/24"<br>}</pre> | no |
| cdir\_private\_2 | CIDR base for private subnet 2 | `map` | <pre>{<br>  "dev": "172.31.87.0/24",<br>  "production": "172.31.91.0/24"<br>}</pre> | no |
| cdir\_public\_1 | CIDR base for public subnet 1 | `map` | <pre>{<br>  "dev": "172.31.84.0/24",<br>  "production": "172.31.88.0/24"<br>}</pre> | no |
| cdir\_public\_2 | CIDR base for public subnet 2 | `map` | <pre>{<br>  "dev": "172.31.85.0/24",<br>  "production": "172.31.89.0/24"<br>}</pre> | no |
| cidr\_base | CIDR base for the environment | `map` | <pre>{<br>  "dev": "172.31.84.0/22",<br>  "production": "172.31.88.0/22"<br>}</pre> | no |
| common\_info | Global Tags # kre infrastructure for mettel-automation project | `map(string)` | <pre>{<br>  "project": "mettel-automation",<br>  "provisioning": "Terraform"<br>}</pre> | no |

## Outputs

| Name | Description |
|------|-------------|
| subnet\_automation-private-1a | Information details about private subnet 1a |
| subnet\_automation-private-1b | Information details about private subnet 1b |
| subnet\_automation-public-1a | Information details about public subnet 1a |
| subnet\_automation-public-1b | Information details about public subnet 1b |
| vpc\_automation\_id | VPC identifier for the environment |


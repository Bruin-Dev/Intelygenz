## Requirements

| Name | Version |
|------|---------|
| terraform | = 0.14.4 |
| aws | =3.26.0 |
| external | = 1.2.0 |
| local | = 1.4.0 |
| null | = 2.1.0 |
| random | = 2.3.0 |
| template | = 2.1.0 |
| tls | = 2.2.0 |

## Providers

| Name | Version |
|------|---------|
| aws | =3.26.0 |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| CURRENT\_ENVIRONMENT | Name of the environment to identify common resources to be used | `string` | `"dev"` | no |
| ENVIRONMENT | Name of the current environment | `string` | `"test"` | no |
| REDIS\_CLUSTER\_NAME | Name of redis cluster | `string` | `"redis"` | no |
| REDIS\_TYPE | Describe type of redis (general or specific\_for\_microservices) | `string` | `"general"` | no |
| common\_info | Global Tags # mettel-automation project | `map(string)` | <pre>{<br>  "project": "mettel-automation",<br>  "provisioning": "Terraform"<br>}</pre> | no |
| redis\_node\_type | Redis node type instance in each environment | `map(map(string))` | <pre>{<br>  "general": {<br>    "dev": "cache.t2.micro",<br>    "production": "cache.m4.large"<br>  },<br>  "specific_for_microservices": {<br>    "dev": "cache.t2.micro",<br>    "production": "cache.t2.small"<br>  }<br>}</pre> | no |

## Outputs

| Name | Description |
|------|-------------|
| REDIS\_HOSTNAME | Hostname of Redis |


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
| helm | = 1.3.2 |
| kubernetes | = 2.0.1 |
| null | = 2.1.0 |
| template | = 2.1.0 |
| tls | = 2.2.0 |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| CURRENT\_ENVIRONMENT | Name of the environment to identify common resources to be used | `string` | `"dev"` | no |
| EXTERNAL\_DNS\_HELM\_CHART\_VERSION | Helm chart version used for external-dns | `string` | `"4.8.6"` | no |
| GRAFANA\_ADMIN\_PASSWORD | Grafana admin password | `string` | `""` | no |
| GRAFANA\_ADMIN\_USER | Grafana admin user | `string` | `""` | no |
| INGRESS\_NGINX\_HELM\_CHART\_VERSION | Helm chart version used for ingress-nginx | `string` | `"3.21.0"` | no |
| METRICS\_SERVER\_VERSION | Version of metrics server release to install in the EKS cluster | `string` | `"0.4.2"` | no |
| RELOADER\_CHART\_VERSION | Helm chart version used for reloader | `string` | `"0.0.81"` | no |
| WHITELISTED\_IPS | Allowed IPs to access Load Balancer created by nginx ingress controller | `list(string)` | <pre>[<br>  ""<br>]</pre> | no |
| common\_info | Global Tags # mettel-automation project | `map(string)` | <pre>{<br>  "project": "mettel-automation",<br>  "provisioning": "Terraform"<br>}</pre> | no |
| map\_users | Additional IAM users to add to the aws-auth configmap. | <pre>list(object({<br>    userarn  = string<br>    username = string<br>    groups   = list(string)<br>  }))</pre> | <pre>[<br>  {<br>    "groups": [<br>      "system:masters"<br>    ],<br>    "userarn": "arn:aws:iam::374050862540:user/angel.costales",<br>    "username": "angel.costales"<br>  }<br>]</pre> | no |
| worker\_node\_instance\_type | n/a | `map(string)` | <pre>{<br>  "dev": "m5.large",<br>  "production": "m5.large"<br>}</pre> | no |

## Outputs

No output.


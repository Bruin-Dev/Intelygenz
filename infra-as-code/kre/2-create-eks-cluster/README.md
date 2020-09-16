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
| helm | = 1.3.2 |
| null | = 2.1.0 |
| template | = 2.1.0 |
| terraform | n/a |
| tls | = 2.2.0 |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| AWS\_SECRET\_ACCESS\_KEY | AWS Secret Access Key credentials | `string` | `""` | no |
| CERT\_MANAGER\_HELM\_CHART\_VERSION | Helm chart version used for cert-manager | `string` | `"1.2.0"` | no |
| CURRENT\_ENVIRONMENT | Name of the environment to identify common resources to be used | `string` | `"dev"` | no |
| EXTERNAL\_DNS\_HELM\_CHART\_VERSION | Helm chart version used for external-dns | `string` | `"4.8.6"` | no |
| HOSTPATH\_HELM\_CHART\_VERSION | Helm chart version used for hostpath | `string` | `"0.2.3"` | no |
| INGRESS\_NGINX\_HELM\_CHART\_VERSION | Helm chart version used for ingress-nginx | `string` | `"3.21.0"` | no |
| METRICS\_SERVER\_VERSION | Version of metrics server release to install in the EKS cluster | `string` | `"0.4.2"` | no |
| WHITELISTED\_IPS | Allowed IPs to access Load Balancer created by nginx ingress controller | `list(string)` | <pre>[<br>  ""<br>]</pre> | no |
| common\_info | Global Tags # kre infrastructure for mettel-automation project | `map(string)` | <pre>{<br>  "project": "mettel-automation-kre",<br>  "provisioning": "Terraform"<br>}</pre> | no |
| map\_users | Additional IAM users to add to the aws-auth configmap. | <pre>list(object({<br>    userarn  = string<br>    username = string<br>    groups   = list(string)<br>  }))</pre> | <pre>[<br>  {<br>    "groups": [<br>      "system:masters"<br>    ],<br>    "userarn": "arn:aws:iam::374050862540:user/xoan.mallon",<br>    "username": "xoan.mallon"<br>  }<br>]</pre> | no |

## Outputs

No output.


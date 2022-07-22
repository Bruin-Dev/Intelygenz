## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.1, < 1.2 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | = 3.70.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | = 3.70.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [aws_dx_gateway_association.direct-connect-gateway-vpg-association](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/dx_gateway_association) | resource |
| [aws_eip.automation-nat_eip-1a](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/eip) | resource |
| [aws_eip.automation-nat_eip-1b](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/eip) | resource |
| [aws_internet_gateway.automation-igw](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/internet_gateway) | resource |
| [aws_nat_gateway.automation-nat-1a](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/nat_gateway) | resource |
| [aws_nat_gateway.automation-nat-1b](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/nat_gateway) | resource |
| [aws_route.aiven-to-automation-private-1a](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/route) | resource |
| [aws_route.aiven-to-automation-private-1b](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/route) | resource |
| [aws_route.automation-igw-public-1a](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/route) | resource |
| [aws_route.automation-igw-public-1b](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/route) | resource |
| [aws_route.automation-nat-private-1a](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/route) | resource |
| [aws_route.automation-nat-private-1b](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/route) | resource |
| [aws_route.data-highway-private-1a-to-automation-private-1a](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/route) | resource |
| [aws_route.data-highway-private-1a-to-automation-private-1b](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/route) | resource |
| [aws_route.data-highway-private-1b-to-automation-private-1a](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/route) | resource |
| [aws_route.data-highway-private-1b-to-automation-private-1b](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/route) | resource |
| [aws_route53_zone.automation-private-zone](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/route53_zone) | resource |
| [aws_route_table.automation-private-1a](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/route_table) | resource |
| [aws_route_table.automation-private-1b](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/route_table) | resource |
| [aws_route_table.automation-public-1a](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/route_table) | resource |
| [aws_route_table.automation-public-1b](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/route_table) | resource |
| [aws_route_table_association.automation-private-1a](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/route_table_association) | resource |
| [aws_route_table_association.automation-private-1b](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/route_table_association) | resource |
| [aws_route_table_association.automation-public-1a](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/route_table_association) | resource |
| [aws_route_table_association.automation-public-1b](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/route_table_association) | resource |
| [aws_s3_bucket.bucket_eks_cluster](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/s3_bucket) | resource |
| [aws_security_group.automation-default](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/security_group) | resource |
| [aws_subnet.automation-private_subnet-1a](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/subnet) | resource |
| [aws_subnet.automation-private_subnet-1b](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/subnet) | resource |
| [aws_subnet.automation-public_subnet-1a](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/subnet) | resource |
| [aws_subnet.automation-public_subnet-1b](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/subnet) | resource |
| [aws_vpc.automation-vpc](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/vpc) | resource |
| [aws_vpn_gateway.vpn_gw](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/vpn_gateway) | resource |
| [aws_dx_gateway.direct-connect-gateway](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/data-sources/dx_gateway) | data source |
| [aws_vpc_peering_connection.data-highway-aiven-peering-connection](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/data-sources/vpc_peering_connection) | data source |
| [aws_vpc_peering_connection.data-highway-peering-connection](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/data-sources/vpc_peering_connection) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_AIVEN_CIDR"></a> [AIVEN\_CIDR](#input\_AIVEN\_CIDR) | Aiven CIRD nets blocks | `string` | `"10.1.0.0/24"` | no |
| <a name="input_CURRENT_ENVIRONMENT"></a> [CURRENT\_ENVIRONMENT](#input\_CURRENT\_ENVIRONMENT) | Name of the environment to identify common resources to be used | `string` | `"dev"` | no |
| <a name="input_DATA_HIGHWAY_AIVEN_PEERING_CONNECTION_ID"></a> [DATA\_HIGHWAY\_AIVEN\_PEERING\_CONNECTION\_ID](#input\_DATA\_HIGHWAY\_AIVEN\_PEERING\_CONNECTION\_ID) | VPC PEERING connection ID between data highway aiven and automation nets | `string` | n/a | yes |
| <a name="input_DATA_HIGHWAY_CIDR_PRIVATE_1A"></a> [DATA\_HIGHWAY\_CIDR\_PRIVATE\_1A](#input\_DATA\_HIGHWAY\_CIDR\_PRIVATE\_1A) | Private subnet A CIDR of data highway project | `map(string)` | <pre>{<br>  "dev": "172.31.78.0/24",<br>  "production": "172.31.74.0/24"<br>}</pre> | no |
| <a name="input_DATA_HIGHWAY_CIDR_PRIVATE_1B"></a> [DATA\_HIGHWAY\_CIDR\_PRIVATE\_1B](#input\_DATA\_HIGHWAY\_CIDR\_PRIVATE\_1B) | Private subnet B CIDR of data highway project | `map(string)` | <pre>{<br>  "dev": "172.31.79.0/24",<br>  "production": "172.31.75.0/24"<br>}</pre> | no |
| <a name="input_DATA_HIGHWAY_PEERING_CONNECTION_ID"></a> [DATA\_HIGHWAY\_PEERING\_CONNECTION\_ID](#input\_DATA\_HIGHWAY\_PEERING\_CONNECTION\_ID) | VPC PEERING connection ID between data highway and automation nets | `string` | n/a | yes |
| <a name="input_EKS_CLUSTER_NAMES"></a> [EKS\_CLUSTER\_NAMES](#input\_EKS\_CLUSTER\_NAMES) | Name of the EKS cluster to allow deploy its ELB in the public subnets | `map` | <pre>{<br>  "dev": [<br>    "mettel-automation-kre-dev",<br>    "mettel-automation-dev"<br>  ],<br>  "production": [<br>    "mettel-automation-kre",<br>    "mettel-automation"<br>  ]<br>}</pre> | no |
| <a name="input_EKS_KRE_BASE_NAME"></a> [EKS\_KRE\_BASE\_NAME](#input\_EKS\_KRE\_BASE\_NAME) | Base name used for EKS cluster used to deploy kre component | `string` | `"mettel-automation-kre"` | no |
| <a name="input_EKS_PROJECT_BASE_NAME"></a> [EKS\_PROJECT\_BASE\_NAME](#input\_EKS\_PROJECT\_BASE\_NAME) | Base name used for EKS cluster used to deploy project components | `string` | `"mettel-automation"` | no |
| <a name="input_cdir_private_1"></a> [cdir\_private\_1](#input\_cdir\_private\_1) | CIDR base for private subnet 1 | `map` | <pre>{<br>  "dev": "172.31.86.0/24",<br>  "production": "172.31.90.0/24"<br>}</pre> | no |
| <a name="input_cdir_private_2"></a> [cdir\_private\_2](#input\_cdir\_private\_2) | CIDR base for private subnet 2 | `map` | <pre>{<br>  "dev": "172.31.87.0/24",<br>  "production": "172.31.91.0/24"<br>}</pre> | no |
| <a name="input_cdir_public_1"></a> [cdir\_public\_1](#input\_cdir\_public\_1) | CIDR base for public subnet 1 | `map` | <pre>{<br>  "dev": "172.31.84.0/24",<br>  "production": "172.31.88.0/24"<br>}</pre> | no |
| <a name="input_cdir_public_2"></a> [cdir\_public\_2](#input\_cdir\_public\_2) | CIDR base for public subnet 2 | `map` | <pre>{<br>  "dev": "172.31.85.0/24",<br>  "production": "172.31.89.0/24"<br>}</pre> | no |
| <a name="input_cidr_base"></a> [cidr\_base](#input\_cidr\_base) | CIDR base for the environment | `map` | <pre>{<br>  "dev": "172.31.84.0/22",<br>  "production": "172.31.88.0/22"<br>}</pre> | no |
| <a name="input_common_info"></a> [common\_info](#input\_common\_info) | Global Tags # mettel-automation project | `map(string)` | <pre>{<br>  "project": "mettel-automation",<br>  "provisioning": "Terraform"<br>}</pre> | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_subnet_automation-private-1a"></a> [subnet\_automation-private-1a](#output\_subnet\_automation-private-1a) | Information details about private subnet 1a |
| <a name="output_subnet_automation-private-1b"></a> [subnet\_automation-private-1b](#output\_subnet\_automation-private-1b) | Information details about private subnet 1b |
| <a name="output_subnet_automation-public-1a"></a> [subnet\_automation-public-1a](#output\_subnet\_automation-public-1a) | Information details about public subnet 1a |
| <a name="output_subnet_automation-public-1b"></a> [subnet\_automation-public-1b](#output\_subnet\_automation-public-1b) | Information details about public subnet 1b |
| <a name="output_vpc_automation_id"></a> [vpc\_automation\_id](#output\_vpc\_automation\_id) | VPC identifier for the environment |

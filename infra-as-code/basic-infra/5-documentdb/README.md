## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.1, < 1.2 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | =3.47.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | =3.47.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [aws_db_subnet_group.db_subnet_group](https://registry.terraform.io/providers/hashicorp/aws/3.47.0/docs/resources/db_subnet_group) | resource |
| [aws_docdb_cluster.docdb](https://registry.terraform.io/providers/hashicorp/aws/3.47.0/docs/resources/docdb_cluster) | resource |
| [aws_docdb_cluster_instance.data_collector_docdb_instance_1](https://registry.terraform.io/providers/hashicorp/aws/3.47.0/docs/resources/docdb_cluster_instance) | resource |
| [aws_docdb_cluster_instance.data_collector_docdb_instance_2](https://registry.terraform.io/providers/hashicorp/aws/3.47.0/docs/resources/docdb_cluster_instance) | resource |
| [aws_docdb_cluster_parameter_group.docdb_parameter_group](https://registry.terraform.io/providers/hashicorp/aws/3.47.0/docs/resources/docdb_cluster_parameter_group) | resource |
| [aws_security_group.docdb_security_group](https://registry.terraform.io/providers/hashicorp/aws/3.47.0/docs/resources/security_group) | resource |
| [aws_subnet.mettel-automation-private-subnet-1a](https://registry.terraform.io/providers/hashicorp/aws/3.47.0/docs/data-sources/subnet) | data source |
| [aws_subnet.mettel-automation-private-subnet-1b](https://registry.terraform.io/providers/hashicorp/aws/3.47.0/docs/data-sources/subnet) | data source |
| [aws_subnet_ids.mettel-automation-private-subnets](https://registry.terraform.io/providers/hashicorp/aws/3.47.0/docs/data-sources/subnet_ids) | data source |
| [aws_subnet_ids.mettel-automation-public-subnets](https://registry.terraform.io/providers/hashicorp/aws/3.47.0/docs/data-sources/subnet_ids) | data source |
| [aws_vpc.mettel-automation-vpc](https://registry.terraform.io/providers/hashicorp/aws/3.47.0/docs/data-sources/vpc) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_CURRENT_ENVIRONMENT"></a> [CURRENT\_ENVIRONMENT](#input\_CURRENT\_ENVIRONMENT) | current environment | `string` | `"dev"` | no |
| <a name="input_TICKET_COLLECTOR_MONGO_PASSWORD"></a> [TICKET\_COLLECTOR\_MONGO\_PASSWORD](#input\_TICKET\_COLLECTOR\_MONGO\_PASSWORD) | DocumentDB main password | `string` | `"mypassword"` | no |
| <a name="input_TICKET_COLLECTOR_MONGO_USERNAME"></a> [TICKET\_COLLECTOR\_MONGO\_USERNAME](#input\_TICKET\_COLLECTOR\_MONGO\_USERNAME) | DocumentDB main username | `string` | `"myusername"` | no |
| <a name="input_cdir_private_1"></a> [cdir\_private\_1](#input\_cdir\_private\_1) | CIDR base for private subnet 1 | `map` | <pre>{<br>  "dev": "172.31.86.0/24",<br>  "production": "172.31.90.0/24"<br>}</pre> | no |
| <a name="input_cdir_private_2"></a> [cdir\_private\_2](#input\_cdir\_private\_2) | CIDR base for private subnet 2 | `map` | <pre>{<br>  "dev": "172.31.87.0/24",<br>  "production": "172.31.91.0/24"<br>}</pre> | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_ticket-collector-mongo-host"></a> [ticket-collector-mongo-host](#output\_ticket-collector-mongo-host) | n/a |

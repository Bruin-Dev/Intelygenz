## Requirements

| Name | Version |
|------|---------|
| aws | =3.9.0 |
| external | = 1.2 |
| null | = 2.1 |
| template | = 2.1 |

## Providers

| Name | Version |
|------|---------|
| aws | =3.9.0 |
| null | = 2.1 |
| terraform | n/a |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| CURRENT\_ENVIRONMENT | Name of the environment to identify the network resources to be used | `string` | `"dev"` | no |
| DOCDB\_CLUSTER\_MASTER\_PASSWORD | Password for the master DB user | `string` | `"test"` | no |
| DOCDB\_CLUSTER\_MASTER\_USERNAME | Username for the master DB user | `string` | `"mast"` | no |
| REST\_API\_DATA\_COLLECTOR\_AUTH\_TOKEN | Auth token used in data-collector lambda function | `string` | `""` | no |
| REST\_API\_DATA\_COLLECTOR\_MONGODB\_COLLECTION | MongoDB's collection used by the lambda data-collector | `string` | `"data"` | no |
| REST\_API\_DATA\_COLLECTOR\_MONGODB\_DATABASE | MongoDB's database used by the lambda data-collector | `string` | `"db"` | no |
| REST\_API\_DATA\_COLLECTOR\_MONGODB\_QUERYSTRING | MongoDB's querystring | `string` | `"ssl=true&ssl_ca_certs=rds-combined-ca-bundle.pem&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false"` | no |
| docdb\_instance\_class\_data-collector | Instance class used for DocumentDB used by data-collector lambda | `string` | `"db.t3.medium"` | no |

## Outputs

| Name | Description |
|------|-------------|
| api\_gateway\_endpoint\_data\_collector | n/a |


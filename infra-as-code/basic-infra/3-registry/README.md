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

| Name                                                                                                                                                                          | Type     |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| [aws_ecr_lifecycle_policy.bruin-bridge-image-lifecycle](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_lifecycle_policy)                     | resource |
| [aws_ecr_lifecycle_policy.customer-cache-image-lifecycle](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_lifecycle_policy)                   | resource |
| [aws_ecr_lifecycle_policy.digi-bridge-image-lifecycle](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_lifecycle_policy)                      | resource |
| [aws_ecr_lifecycle_policy.digi-reboot-report-image-lifecycle](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_lifecycle_policy)               | resource |
| [aws_ecr_lifecycle_policy.dri-bridge-image-lifecycle](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_lifecycle_policy)                       | resource |
| [aws_ecr_lifecycle_policy.email-tagger-kre-bridge-image-lifecycle](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_lifecycle_policy)          | resource |
| [aws_ecr_lifecycle_policy.email-tagger-monitor-image-lifecycle](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_lifecycle_policy)             | resource |
| [aws_ecr_lifecycle_policy.fraud-monitor-image-lifecycle](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_lifecycle_policy)                    | resource |
| [aws_ecr_lifecycle_policy.hawkeye-affecting-monitor-image-lifecycle](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_lifecycle_policy)        | resource |
| [aws_ecr_lifecycle_policy.hawkeye-bridge-image-lifecycle](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_lifecycle_policy)                   | resource |
| [aws_ecr_lifecycle_policy.hawkeye-customer-cache-image-lifecycle](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_lifecycle_policy)           | resource |
| [aws_ecr_lifecycle_policy.hawkeye-outage-monitor-image-lifecycle](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_lifecycle_policy)           | resource |
| [aws_ecr_lifecycle_policy.intermapper-outage-monitor-image-lifecycle](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_lifecycle_policy)       | resource |
| [aws_ecr_lifecycle_policy.last-contact-report-image-lifecycle](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_lifecycle_policy)              | resource |
| [aws_ecr_lifecycle_policy.links-metrics-api-image-lifecycle](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_lifecycle_policy)                | resource |
| [aws_ecr_lifecycle_policy.links-metrics-collector-image-lifecycle](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_lifecycle_policy)          | resource |
| [aws_ecr_lifecycle_policy.lumin-billing-report-image-lifecycle](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_lifecycle_policy)             | resource |
| [aws_ecr_lifecycle_policy.notifier-image-lifecycle](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_lifecycle_policy)                         | resource |
| [aws_ecr_lifecycle_policy.notifications-bridge-image-lifecycle](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_lifecycle_policy)             | resource |
| [aws_ecr_lifecycle_policy.repair-tickets-kre-bridge-image-lifecycle](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_lifecycle_policy)        | resource |
| [aws_ecr_lifecycle_policy.repair-tickets-monitor-image-lifecycle](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_lifecycle_policy)           | resource |
| [aws_ecr_lifecycle_policy.service-affecting-monitor-image-lifecycle](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_lifecycle_policy)        | resource |
| [aws_ecr_lifecycle_policy.service-outage-monitor-image-lifecycle](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_lifecycle_policy)           | resource |
| [aws_ecr_lifecycle_policy.t7-bridge-image-lifecycle](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_lifecycle_policy)                        | resource |
| [aws_ecr_lifecycle_policy.ticket-collector-image-lifecycle](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_lifecycle_policy)                 | resource |
| [aws_ecr_lifecycle_policy.ticket-statistics-image-lifecycle](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_lifecycle_policy)                | resource |
| [aws_ecr_lifecycle_policy.tnba-feedback-image-lifecycle](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_lifecycle_policy)                    | resource |
| [aws_ecr_lifecycle_policy.tnba-monitor-image-lifecycle](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_lifecycle_policy)                     | resource |
| [aws_ecr_lifecycle_policy.velocloud-bridge-image-lifecycle](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_lifecycle_policy)                 | resource |
| [aws_ecr_repository.bruin-bridge-repository](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository)                                      | resource |
| [aws_ecr_repository.customer-cache-repository](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository)                                    | resource |
| [aws_ecr_repository.digi-bridge-repository](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository)                                       | resource |
| [aws_ecr_repository.digi-reboot-report-repository](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository)                                | resource |
| [aws_ecr_repository.dri-bridge-repository](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository)                                        | resource |
| [aws_ecr_repository.email-tagger-kre-bridge-repository](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository)                           | resource |
| [aws_ecr_repository.email-tagger-monitor-repository](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository)                              | resource |
| [aws_ecr_repository.fraud-monitor-repository](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository)                                     | resource |
| [aws_ecr_repository.hawkeye-affecting-monitor-repository](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository)                         | resource |
| [aws_ecr_repository.hawkeye-bridge-repository](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository)                                    | resource |
| [aws_ecr_repository.hawkeye-customer-cache-repository](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository)                            | resource |
| [aws_ecr_repository.hawkeye-outage-monitor-repository](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository)                            | resource |
| [aws_ecr_repository.intermapper-outage-monitor-repository](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository)                        | resource |
| [aws_ecr_repository.last-contact-report-repository](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository)                               | resource |
| [aws_ecr_repository.links-metrics-api-repository](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository)                                 | resource |
| [aws_ecr_repository.links-metrics-collector-repository](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository)                           | resource |
| [aws_ecr_repository.lumin-billing-report-repository](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository)                              | resource |
| [aws_ecr_repository.notifier-repository](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository)                                          | resource |
| [aws_ecr_repository.notifications-bridge-repository](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository)                              | resource |
| [aws_ecr_repository.repair-tickets-kre-bridge-repository](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository)                         | resource |
| [aws_ecr_repository.repair-tickets-monitor-repository](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository)                            | resource |
| [aws_ecr_repository.service-affecting-monitor-repository](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository)                         | resource |
| [aws_ecr_repository.service-outage-monitor-repository](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository)                            | resource |
| [aws_ecr_repository.t7-bridge-repository](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository)                                         | resource |
| [aws_ecr_repository.ticket-collector-repository](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository)                                  | resource |
| [aws_ecr_repository.ticket-statistics-repository](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository)                                 | resource |
| [aws_ecr_repository.tnba-feedback-repository](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository)                                     | resource |
| [aws_ecr_repository.tnba-monitor-repository](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository)                                      | resource |
| [aws_ecr_repository.velocloud-bridge-repository](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository)                                  | resource |
| [aws_ecr_repository_policy.bruin-bridge-fedramp-pull-policy](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository_policy)               | resource |
| [aws_ecr_repository_policy.customer-cache-fedramp-pull-policy](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository_policy)             | resource |
| [aws_ecr_repository_policy.digi-bridge-fedramp-pull-policy](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository_policy)                | resource |
| [aws_ecr_repository_policy.digi-reboot-report-fedramp-pull-policy](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository_policy)         | resource |
| [aws_ecr_repository_policy.dri-bridge-fedramp-pull-policy](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository_policy)                 | resource |
| [aws_ecr_repository_policy.email-tagger-kre-bridge-fedramp-pull-policy](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository_policy)    | resource |
| [aws_ecr_repository_policy.email-tagger-monitor-fedramp-pull-policy](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository_policy)       | resource |
| [aws_ecr_repository_policy.fraud-monitor-fedramp-pull-policy](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository_policy)              | resource |
| [aws_ecr_repository_policy.hawkeye-affecting-monitor-fedramp-pull-policy](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository_policy)  | resource |
| [aws_ecr_repository_policy.hawkeye-bridge-fedramp-pull-policy](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository_policy)             | resource |
| [aws_ecr_repository_policy.hawkeye-customer-cache-fedramp-pull-policy](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository_policy)     | resource |
| [aws_ecr_repository_policy.hawkeye-outage-monitor-fedramp-pull-policy](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository_policy)     | resource |
| [aws_ecr_repository_policy.intermapper-outage-monitor-fedramp-pull-policy](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository_policy) | resource |
| [aws_ecr_repository_policy.last-contact-report-fedramp-pull-policy](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository_policy)        | resource |
| [aws_ecr_repository_policy.links-metrics-api-fedramp-pull-policy](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository_policy)          | resource |
| [aws_ecr_repository_policy.links-metrics-collector-fedramp-pull-policy](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository_policy)    | resource |
| [aws_ecr_repository_policy.lumin-billing-report-fedramp-pull-policy](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository_policy)       | resource |
| [aws_ecr_repository_policy.notifier-fedramp-pull-policy](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository_policy)                   | resource |
| [aws_ecr_repository_policy.notifications-bridge-fedramp-pull-policy](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository_policy)       | resource |
| [aws_ecr_repository_policy.repair-tickets-kre-bridge-fedramp-pull-policy](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository_policy)  | resource |
| [aws_ecr_repository_policy.repair-tickets-monitor-fedramp-pull-policy](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository_policy)     | resource |
| [aws_ecr_repository_policy.service-affecting-monitor-fedramp-pull-policy](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository_policy)  | resource |
| [aws_ecr_repository_policy.service-outage-monitor-fedramp-pull-policy](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository_policy)     | resource |
| [aws_ecr_repository_policy.t7-bridge-fedramp-pull-policy](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository_policy)                  | resource |
| [aws_ecr_repository_policy.ticket-collector-fedramp-pull-policy](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository_policy)           | resource |
| [aws_ecr_repository_policy.ticket-statistics-fedramp-pull-policy](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository_policy)          | resource |
| [aws_ecr_repository_policy.tnba-feedback-fedramp-pull-policy](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository_policy)              | resource |
| [aws_ecr_repository_policy.tnba-monitor-fedramp-pull-policy](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository_policy)               | resource |
| [aws_ecr_repository_policy.velocloud-bridge-fedramp-pull-policy](https://registry.terraform.io/providers/hashicorp/aws/3.70.0/docs/resources/ecr_repository_policy)           | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_CURRENT_ENVIRONMENT"></a> [CURRENT\_ENVIRONMENT](#input\_CURRENT\_ENVIRONMENT) | Name of the environment to identify common resources to be used | `string` | `"dev"` | no |
| <a name="input_FEDERAL_ACCOUNT_ID"></a> [FEDERAL\_ACCOUNT\_ID](#input\_FEDERAL\_ACCOUNT\_ID) | Account ID of Federal AWS account | `string` | `"663771866250"` | no |
| <a name="input_common_info"></a> [common\_info](#input\_common\_info) | Global Tags # mettel-automation project | `map(string)` | <pre>{<br>  "project": "mettel-automation",<br>  "provisioning": "Terraform"<br>}</pre> | no |

## Outputs

No outputs.

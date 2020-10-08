# Route53 utils

A number of scripts developed in bash for naming environments are stored in this folder.

**Table of contents**:
- [nginx_ingress_route53_util](#nginx_ingress_route53_util-cli)
  - [Description](#description)
  - [Usage](#usage)

## nginx_ingress_route53_util cli

### Description

This [cli](./nginx_ingress_route53_util.py) has been developed in python for create/update a route in a hosted zone of Route53 for an alias of the ELB created by [nginx ingress](https://github.com/helm/charts/tree/master/stable/nginx-ingress).

### Usage

In order to use this [script](./nginx_ingress_route53_util.py) it is necessary to perform the following steps previously:

- Define the AWS credentials, for this it is necessary to define the environment variables `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_DEFAULT_REGION` in the following way:

    ```sh
    $ export AWS_ACCESS_KEY_ID=<access_key>
    $ export AWS_SECRET_ACCESS_KEY=<secret_key>
    $ export AWS_DEFAULT_REGION=<aws_region>
    ```
    > The default AWS region used in the project is us-east-1
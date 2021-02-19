# Route53 utils

A number of scripts developed in *Python* for working with [Route53](https://aws.amazon.com/route53/) Service of AWS are stored in this folder.

**Table of contents**:
- [nginx_ingress_route53_util](#nginx_ingress_route53_util-cli)
  - [Description](#description)
  - [Usage](#usage)
  - [Execution example](#execution-example)
- [delete_hosted_zones](#delete_hosted_zones)
  - [Description](#description-1)
  - [Usage](#usage-1)
  - [Execution example](#execution-example-1)

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

- Configure the [kubeconfig](https://kubernetes.io/docs/concepts/configuration/organize-cluster-access-kubeconfig/) file, specifically in `$HOME/.kube/config` with the Kubernetes cluster on which you want to obtain the ELB created by nginx ingress.

  Below is an example:
  ```sh
  apiVersion: v1
  clusters:
    - cluster:
          certificate-authority: /home/<user>/.minikube/ca.crt
          server: https://172.17.0.2:8443
      name: minikube
  contexts:
    - context:
          cluster: minikube
          user: minikube
      name: minikube
  current-context: minikube
  kind: Config
  preferences: {}
  users:
    - name: minikube
      user:
          client-certificate: /home/<user>/.minikube/profiles/minikube/client.crt
          client-key: /home/<user>.minikube/profiles/minikube/client.key
  ```

- Install the python packages required by the cli, these are specified in the `requirements.txt` file and are installed through the following command:

  ```sh
  $ pip3 install -r requirements.txt
  ```

- Once the previous steps has been followed, it is possible to use the cli in the following way:

  ```sh
  $ python3 nginx_ingress_route53_util.py -a/--record_alias_name <record_alias_name> -n/--hosted_zone_name <hosted_zone_name> -u/--update <update_value> -d/--delete <delete_value>
  ```

  - `-a/--record_alias_name`: Parameter used to indicate the value of the record set in Route53 with the ELB alias created by nginx ingress.

  - `-n/--hosted_zone_name`: Parameter used to indicate the name of the hosted zone in Route53 where the alias of the ELB will be created.

  - `-u/--update`: Boolean flag to indicate if the ELB record set is to be created or updated in the indicated hosted zone.

  - `-d/--delete`: Boolean flag to indicate if the ELB record set is to be deleted in the indicated hosted zone.

  > It is only possible to indicate the value 'True' for one of the parameters 'u/--update' or 'd/--delete'.

### Execution example

The following is an example of the execution of this cli:

```sh
$ python3 nginx_ingress_route53_util.py -a "*.kre-dev.mettel-automation.net." -n "kre-dev.mettel-automation.net." -u True
```

## delete_hosted_zones

### Description
This [cli](./delete_hosted_zones.py) has been developed in python for delete all records with different type of NS and SOA in a specific hosted zone of Route53

### Usage

In order to use this [script](./delete_hosted_zones.py) it is necessary to perform the following steps previously:

- Define the AWS credentials, for this it is necessary to define the environment variables `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_DEFAULT_REGION` in the following way:

    ```sh
    $ export AWS_ACCESS_KEY_ID=<access_key>
    $ export AWS_SECRET_ACCESS_KEY=<secret_key>
    $ export AWS_DEFAULT_REGION=<aws_region>
    ```
    > The default AWS region used in the project is us-east-1

- Install the python packages required by the cli, these are specified in the `requirements.txt` file and are installed through the following command:

  ```sh
  $ pip3 install -r requirements.txt
  ```

- Once the previous steps has been followed, it is possible to use the cli in the following way:

  ```sh
  $ python3 nginx_ingress_route53_util.py -a/--record_alias_name <record_alias_name> -n/--hosted_zone_name <hosted_zone_name> -u/--update <update_value> -d/--delete <delete_value>
  ```

  - `-n/--hosted_zone_name`: Parameter used to indicate the name of the hosted zone in Route53 where the alias of the ELB will be created

### Execution example

The following is an example of the execution of this cli:

```sh
$ python3 delete_hosted_zones.py -n "kre-dev.mettel-automation.net."
```
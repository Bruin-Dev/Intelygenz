# ci-utils

In this folder are stored a series of scripts implemented in bash and python used as tools for the CI/CD process, these will be detailed in the sections shown below.

**Table of content:**

+ [Task_healtcheck](#task_healthcheck)
    - [Description](#task_healthcheck_description)
    - [Usage](#task_healthcheck_usage)
+ [Grafana_users_creation](#grafana_users_creation)
    - [Description](#grafana_users_creation_description)
    - [Usage](#grafana_users_creation_usae)
+ [Script utils delete_environments_aws_resources](#script_utils-delete_environments_aws_resources)
    - [Description](#delete_environments_aws_resources_description)
    - [Usage](#delete_environments_aws_resources_usage)
    - [Commands](#delete_environments_aws_resources_commands)
+ [Aws_nuke_conf_generator](#aws_nuke_conf_generator)
    - [Description](#aws_nuke_conf_generator_description)
    - [Usage](#aws_nuke_conf_generator_usage)

## Script task_healtheck<a name="task_healthcheck"></a>

### Description <a name="task_healthcheck_description"></a>

This [script](./task_healthcheck.sh) has been implemented in *shell scripting*, it is used to check if for a service of a given ECS cluster the last task definition relative to a service provided as parameter is being executed, as well as if it has a `HEALTHY` state.

This script loads the content of [another script](./common_functions.sh), where a series of util functions are declared being able to use them during its execution.

### Usage <a name="task_healthcheck_usage"></a>

In order to use this [script](./task_healthcheck.sh) it is necessary to perform the following steps previously:

* Define the AWS credentials, for this it is necessary to define the environment variables `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in the following way:

    ```sh
    $ export AWS_ACCESS_KEY_ID=<access_key>
    $ export AWS_SECRET_ACCESS_KEY=<secret_key>
    ```

* Declare the variable `TF_VAR_ENVIRONMENT` with the value of the ECS cluster on which you it is going to to used in the following way:

    ```sh
    $ export TF_VAR_ENVIRONMENT=<environment_name>
    ```

    >It is important to remember that the names for environments are `automation-master` for production, as well as `automation-<branch_identifier>` for ephemeral environments, being `branch_identifier` the result of applying `echo -n "<branch_name>" | sha256sum | cut -c1-8` on the branch name related to the ephemeral environment.

Once the previous steps have been carried out, it is possible to use this [script](./task_healthcheck.sh) providing as parameter `-t` the name of the service on which you want to perform the check performed by the script explained above, as shown below:

```sh
$ /bin/bash ci-utils/task_healthcheck.sh -t <service_name>
```

## Script grafana_users_creation<a name="grafana_users_creation"></a>

### Description <a name="grafana_users_creation_description"></a>

[This script](./grafana_users_creation.py) has been implemented in *Python*, it is used for the creation of users in the Grafana service running in a cluster of ECS provided relative to a previously deployed environment. Apart from creating users, the script will assign each one different permissions based on Gitlab's environment variables.

To create users, a series of https calls will be made to the endpoint exposed by the Route53 service of AWS for the backend service in the given environment.

### Usage <a name="grafana_users_creation_usage"></a>

To use this script it is necessary to declare a series of variables, exposed below:

* `ENVIRONMENT_SLUG`: Name of the branch relative to the environment where the script it's going to be used.

  >It is important to remember that for all environments other than production (`master` branch) it is necessary to apply the function `echo -n "<branch_name>" | sha256sum | cut -c1-8` on the branch name

* `GRAFANA_ADMIN_PASSWORD`: Password for the administrator user for the Grafana service related to the environment

* `GRAFANA_ADMIN_USER`: User name for the administrator user for the Grafana service related to the environment

* `GRAFANA_USER_EMAIL`: List of user emails separated by commas to use as an email field in the process of creating them in the Grafana service related to the environment

* `GRAFANA_USER_LOGIN`: List of user logins separated by commas to use as a login field in the process of creating them in the Grafana service related to the environment

* `GRAFANA_USER_NAME`: List of user names separated by commas to use as a user name field in the process of creating them in the Grafana service related to the environment

* `GRAFANA_USER_PASSWORD`: List of user password separated by commas to use as a user password field in the process of creating them in the Grafana service related to the environment

* `GRAFANA_USER_ROLE`: List of user roles separated by commas to use as a user role field in the process of creating them in the Grafana service related to the environment. Valid values are `viewer`, `editor` and `admin`

* `GRAFANA_USER_COMPANY`: List of user companies separated by commas to use as a user company field in the process of creating them in the Grafana service related to the environment

>The number of elements that must have the variables `GRAFANA_USER_EMAIL`, `GRAFANA_USER_LOGIN`, `GRAFANA_USER_NAME`, `GRAFANA_USER_PASSWORD`, `GRAFANA_USER_ROLE` and `GRAFANA_USER_COMPANY` must be the same, since it is necessary to have all the fields related to the users to be created to be able to do it.

## Script utils delete_environments_aws_resources <a name="script_utils-delete_environments_aws_resources"></a>

### Description <a name="delete_environments_aws_resources_description"></a>

In the folder [`delete_environments_aws_resources`](./delete_environments_aws_resources) a series of *Python* files are stored, these allow the deletion of the resources created in AWS associated to an environment.

>It is important to remember that the names for environments are `automation-master` for production, as well as `automation-<branch_identifier>` for ephemeral environments, being `branch_identifier` the result of applying `echo -n "<branch_name>" | sha256sum | cut -c1-8` on the branch name related to the ephemeral environment.

### Usage <a name="delete_environments_aws_resources_usage"></a>

In order to be able to use the CLI mentioned previously it is necessary to previously define the AWS credentials, for this it is necessary to define the environment variables `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in the following way:

```sh
$ export AWS_ACCESS_KEY_ID=<access_key>
$ export AWS_SECRET_ACCESS_KEY=<secret_key>
```

Once the AWS credentials have been configured, it is possible to use the script in the following way:

```bash
python ci-utils/delete_environments_aws_resources/main.py -e <environment_name> [commands]
```
>To use any command it's necessary to specify the environment name as the first argument of the `main.py` script through the -e parameter.

### Commands <a name="delete_environments_aws_resources_commands"></a>

CLI supports a number of commands. These are explained below:

* `-a`, `--all`: All the resources in AWS associated to the specified environment will be deleted, carrying out the corresponding orderly deletion of them so as not to produce dependency errors during the process.

    >**If this option is specified, any other option will be ignored.**
* `-c`, `--ecs-cluster`: The ECS cluster associated to the environment provided will be removed, as well as all the resources related to it:
  
  * *ECS Services* defined in the ECS cluster and *Tasks* of each one of them.
  
  * *Namespaces* and *Services* associated with the same to perform [*Services Discovery*](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-discovery.html) in the cluster

* `-d`, `--service-discovery`: The *namespace* created for the *Service Discovery* of the environment provided will be deleted, previously all the services associated to that namespace will be deleted.

* `-r`, `--redis-cluster`: The *ElastiCache Redis Cluster* associated to the specified environment will be removed.

* `-l`, `--load-balancer`: The *Application Load Balancer (ALB)* associated to the specified environment will be removed, as well as all the resources related to it (*Target Groups*).

* `-s`, `--security-groups`: All the *Security Groups* associated to the different resources created in *AWS* for the specified environment will be removed.

* `-m`, `--metrics`: All the resources related to metrics created for the specified will be removed, being these the ones specified below:

  * *CloudWatch Alarms*
  
  * *CloudWatch Dashboard*

  * *CloudWatch Log Filters*

* `-z`, `--hosted-zones`: All the record set created for specified environment in hosted zone with name `mettel-automation.net` in *AWS Route53 Service* will be deleted.

* `-f`, `--cloud-formation`: The *Cloud Formation Stack* resources created for the specified environment will be removed

* `-b`, `--buckets`: All *Terraform* files with `tfstate` extension related to the specified environment will be deleted, these are used to know the state of the resources created by it and are stored in an  *S3 Bucket* that is specified in the creation of its with *Terraform*.

## Script aws_nuke_conf_generator <a name="aws_nuke_conf_generator"></a>

### Description <a name="aws_nuke_conf_generator_description"></a>

This [script](./aws-nuke/aws_nuke_conf_generator.py) has been implemented to generate the configuration file used by [`aws-nuke`](https://github.com/rebuy-de/aws-nuke) to delete resources in AWS.

The generated configuration file will allow filtering on the resources to be deleted specified in it, so that `aws-nuke` will only delete those associated with the environment specified in that file. The resources to be deleted specified in this file are the following:

* *ElasticacheCacheCluster*
* *ElasticacheSubnetGroup*
* *ELBv2*
* *ELBv2TargetGroup*
* *CloudFormationStack*
* *CloudWatchAlarm*
* *CloudWatchLogsLogGroup*
* *ServiceDiscoveryNamespace*
* *ServiceDiscoveryService*
* *ECSCluster*
* *ECSService*
* *ECSTaskDefinition*
* *EC2SecurityGroup*

In order to carry out this process of generating a configuration file, a [template file](./aws-nuke/config_template.yml) is used on which the script applies the relevant changes to the resources to be filtered.

### Usage <a name="aws_nuke_conf_generator_usage"></a>

In order to be able to use the [script](./aws-nuke/aws_nuke_conf_generator.py) mentioned previously it is necessary to previously define the AWS credentials, for this it is necessary to define the environment variables `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in the following way:

```sh
$ export AWS_ACCESS_KEY_ID=<access_key>
$ export AWS_SECRET_ACCESS_KEY=<secret_key>
```

Once configured the AWS credentials, it is possible to use the [script](./aws-nuke/aws_nuke_conf_generator.py) to create the configuration file that will be used by `aws-nuke` to delete the AWS resources associated to the specified environment, it is necessary to specify this one, using the `-e` option, as shown below:

```sh
$ python ci-utils/aws-nuke/aws_nuke_conf_generator.py -e <environment_name>
```

>It is important to remember that the names for environments are `automation-master` for production, as well as `automation-<branch_identifier>` for ephemeral environments, being `branch_identifier` the result of applying `echo -n "<branch_name>" | sha256sum | cut -c1-8` on the branch name related to the ephemeral environment.
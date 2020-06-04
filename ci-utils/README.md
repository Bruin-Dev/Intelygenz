# ci-utils

In this folder are stored a series of scripts implemented in bash and python used as tools for the CI/CD process, these will be detailed in the sections shown below.

**Table of content:**

- [Task_healtcheck](#task_healthcheck)
  - [Description](#task_healthcheck_description)
  - [Usage](#task_healthcheck_usage)
- [Script utils delete_environments_aws_resources](#script_utils-delete_environments_aws_resources)
  - [Description](#delete_environments_aws_resources_description)
  - [Usage](#delete_environments_aws_resources_usage)
  - [Commands](#delete_environments_aws_resources_commands)
- [Aws_nuke_conf_generator](#aws_nuke_conf_generator)
  - [Description](#aws_nuke_conf_generator_description)
  - [Usage](#aws_nuke_conf_generator_usage)
- [Script check_ecs_resources](#script_check_ecs_resources)
  - [Description](#check_ecs_resources_description)
  - [Usage](#check_ecs_resources_usage)
- [Script manage_ecr_docker_images](#manage_ecr_docker_images)
  - [Description](#manage_ecr_docker_images_description)
  - [Usage](#manage_ecr_docker_images_usage)
- [Papertrail_provisioning](#papertrail_provisioning)
  - [Description](#papertrail_provisioning_description)
  - [Usage](#papertrail_provisioning_usage)

## Script task_healtheck<a name="task_healthcheck"></a>

### Description <a name="task_healthcheck_description"></a>

This [script](./task_healthcheck.sh) has been implemented in *Python*, it is used to check if for a service of a given ECS cluster the given task definition relative to a service provided as parameters is being executed, as well as if it has a `HEALTHY` state.

### Usage <a name="task_healthcheck_usage"></a>

In order to use this [script](./task_healthcheck.py) it is necessary to perform the following steps previously:

- Define the AWS credentials, for this it is necessary to define the environment variables `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in the following way:

    ```sh
    $ export AWS_ACCESS_KEY_ID=<access_key>
    $ export AWS_SECRET_ACCESS_KEY=<secret_key>
    ```

- Declare the variable `TF_VAR_ENVIRONMENT` with the value of the ECS cluster on which you it is going to to used in the following way:

    ```sh
    $ export TF_VAR_ENVIRONMENT=<environment_name>
    ```

    >It is important to remember that the names for environments are `automation-master` for production, as well as `automation-<branch_identifier>` for ephemeral environments, being `branch_identifier` the result of applying `echo -n "<branch_name>" | sha256sum | cut -c1-8` on the branch name related to the ephemeral environment.

- Declare the variable `ECS_MAX_TASKS` with the value of the maximum number of tasks allowed in ECS, currently 100 in the following way:

    ```sh
    $ export ECS_MAX_TASKS=<ecs_max_tasks>
    ```

Once the previous steps have been carried out, it is possible to use this [script](./task_healthcheck.sh) providing as parameter `-t` the name of the service on which you want to perform the check performed by the script explained above, as well as the ARN of the task definition of the service defined in a JSON file as the following parameter, as shown below:

```sh
$ python3 ci-utils/task_healthcheck.py -t <service_name> <task_definition_arn_definition.json>
```

The file <task_definition_arn_definition.json> must comply with the following format:

```json
{
    "taskDefinitionArn": "<task_definition_arn>"
}
```

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

- `-a`, `--all`: All the resources in AWS associated to the specified environment will be deleted, carrying out the corresponding orderly deletion of them so as not to produce dependency errors during the process.

    >**If this option is specified, any other option will be ignored.**
- `-c`, `--ecs-cluster`: The ECS cluster associated to the environment provided will be removed, as well as all the resources related to it:
  
  - *ECS Services* defined in the ECS cluster and *Tasks* of each one of them.
  
  - *Namespaces* and *Services* associated with the same to perform [*Services Discovery*](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-discovery.html) in the cluster

- `-d`, `--service-discovery`: The *namespace* created for the *Service Discovery* of the environment provided will be deleted, previously all the services associated to that namespace will be deleted.

- `-r`, `--redis-cluster`: The *ElastiCache Redis Cluster* associated to the specified environment will be removed.

- `-l`, `--load-balancer`: The *Application Load Balancer (ALB)* associated to the specified environment will be removed, as well as all the resources related to it (*Target Groups*).

- `-s`, `--security-groups`: All the *Security Groups* associated to the different resources created in *AWS* for the specified environment will be removed.

- `-m`, `--metrics`: All the resources related to metrics created for the specified will be removed, being these the ones specified below:

  - *CloudWatch Alarms*
  
  - *CloudWatch Dashboard*

  - *CloudWatch Log Filters*

- `-z`, `--hosted-zones`: All the record set created for specified environment in hosted zone with name `mettel-automation.net` in *AWS Route53 Service* will be deleted.

- `-f`, `--cloud-formation`: The *Cloud Formation Stack* resources created for the specified environment will be removed

- `-b`, `--buckets`: All *Terraform* files with `tfstate` extension related to the specified environment will be deleted, these are used to know the state of the resources created by it and are stored in an  *S3 Bucket* that is specified in the creation of its with *Terraform*.

## Script aws_nuke_conf_generator <a name="aws_nuke_conf_generator"></a>

### Description <a name="aws_nuke_conf_generator_description"></a>

This [script](./aws-nuke/aws_nuke_conf_generator.py) has been implemented to generate the configuration file used by [`aws-nuke`](https://github.com/rebuy-de/aws-nuke) to delete resources in AWS.

The generated configuration file will allow filtering on the resources to be deleted specified in it, so that `aws-nuke` will only delete those associated with the environment specified in that file. The resources to be deleted specified in this file are the following:

- *ElasticacheCacheCluster*
- *ElasticacheSubnetGroup*
- *ELBv2*
- *ELBv2TargetGroup*
- *CloudFormationStack*
- *CloudWatchAlarm*
- *CloudWatchLogsLogGroup*
- *ServiceDiscoveryNamespace*
- *ServiceDiscoveryService*
- *ECSCluster*
- *ECSService*
- *ECSTaskDefinition*
- *EC2SecurityGroup*

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

## Script check_ecs_resources <a name="script_check_ecs_resources"></a>

### Description <a name="check_ecs_resources_description"></a>

This [script](./check_ecs_resources.py) has been implemented in *Python*, it is used for check if there are enough free tasks to create the environment in an AWS ECS cluster before creating infrastructure using Terraform.

### Usage <a name="check_ecs_resources_usage"></a>

In order to use this [script](./check_ecs_resources.py) it is necessary to perform the following steps previously:

- Define the AWS credentials, for this it is necessary to define the environment variables `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in the following way:

    ```sh
    $ export AWS_ACCESS_KEY_ID=<access_key>
    $ export AWS_SECRET_ACCESS_KEY=<secret_key>
    ```

- Declare the variable `TF_VAR_ENVIRONMENT` with the value of the ECS cluster on which you it is going to to used in the following way:

    ```sh
    $ export TF_VAR_ENVIRONMENT=<environment_name>
    ```

    >It is important to remember that the names for environments are `automation-master` for production, as well as `automation-<branch_identifier>` for ephemeral environments, being `branch_identifier` the result of applying `echo -n "<branch_name>" | sha256sum | cut -c1-8` on the branch name related to the ephemeral environment.

Once the previous steps have been carried out, it is possible to use this [script](./check_ecs_resources.py) as shown below:

```sh
$ python3 ci-utils/check_ecs_resources.py
```

## Script manage_ecr_docker_images <a name="manage_ecr_docker_images"></a>

### Description <a name="manage_ecr_docker_images_description"></a>

This [script](./manage_ecr_docker_images_description.py) has been implemented in *Python*, it can be used for any of the following functions:

- Get the oldest image from an ECR repository provided as a parameter in a given environment. In case that repository has more than two images in the provided environment, it will perform the deletion of the oldest image according to the ECR upload date.

- Obtain the most up-to-date image of all the ECR repositories used in the project by saving each one of them in a JSON file for each of the repositories with the following format

   ```bash
   {
       "tag": <ecr_repository_tag>
   }
   ```

### Usage <a name="manage_ecr_docker_images_usage"></a>

In order to use this [script](./manage_ecr_docker_images_description.py) it is necessary to perform the following steps previously:

- Define the AWS credentials, for this it is necessary to define the environment variables `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_DEFAULT_REGION` in the following way:

    ```sh
    $ export AWS_ACCESS_KEY_ID=<access_key>
    $ export AWS_SECRET_ACCESS_KEY=<secret_key>
    $ export AWS_DEFAULT_REGION=<aws_region>
    ```

    > The default AWS region used in the project is us-east-1

- Declare the variable `ENVIRONMENT_VAR` with the value of the environment on which you it is going to to used in the following way:

    ```sh
    $ export ENVIRONMENT_VAR=<environment_name>
    ```

    >It is important to remember that the names for environments are `automation-master` for production, as well as `automation-<branch_identifier>` for ephemeral environments, being `branch_identifier` the result of applying `echo -n "<branch_name>" | sha256sum | cut -c1-8` on the branch name related to the ephemeral environment.

Once the previous steps have been carried out, it is possible to use this [script](./check_ecs_resources.py) as shown below:

- To get the oldest image from a particular repository, provide the name of the repository using the -t option, as follows:

    ```sh
    $ python3 ci-utils/manage_ecr_docker_images.py -r <ecr_repository_name>
    ```

    >The nomenclature of the images in the project is `automation-<microservice_name>`

- To obtain the most up-to-date image for the environment provided in each of the repositories, simply indicate the -g option, as shown below:

   ```sh
   $ python3 ci-utils/manage_ecr_docker_images.py -g
   ```

## Papertrail provisioning <a name="papertrail_provisioning"></a>

### Description <a name="papertrail_provisioning_description"></a>

In the [papertrail_provisioning](./papertrail_provisioning) folder are the utilities to perform the papertrail provisioning for the different microservices of the project in each environment.

### Usage  <a name="papertrail_provisioning_usage"></a>

This utility is intended to be used in the gitlab deployment pipelines for each environment, it uses a configuration file called [config.py](./papertrail_provisioning/config.py) where it will collect the different environment variables needed.

It is possible to add and/or remove papertrail groups, as well as the searches on them by means of the mentioned config.py file, through the modification of the dictionary value named PAPERTRAIL_PROVISIONING.


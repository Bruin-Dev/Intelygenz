# ECS utils

In this folder are stored a series of scripts developed in python to interact with ECS in the CI/CD process.

**Table of contents**:
- [Task_healtcheck](#task_healthcheck)
  - [Description](#task_healthcheck_description)
  - [Usage](#task_healthcheck_usage)
- [Script check_ecs_resources](#script_check_ecs_resources)
  - [Description](#check_ecs_resources_description)
  - [Usage](#check_ecs_resources_usage)
  
## Script task_healtheck<a name="task_healthcheck"></a>

### Description <a name="task_healthcheck_description"></a>

This [script](./task_healthcheck.py) has been implemented in *Python*, it is used to check if for a service of a given ECS cluster the given task definition relative to a service provided as parameters is being executed, as well as if it has a `HEALTHY` state.

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

    Once the previous steps have been carried out, it is possible to use this [script](./task_healthcheck.py) providing as parameter `-t` the name of the service on which you want to perform the check performed by the script explained above, as well as the ARN of the task definition of the service defined in a JSON file as the following parameter, as shown below:
    
    ```sh
    $ python3 ci-utils/ecs/task_healthcheck.py -t <service_name> <task_definition_arn_definition.json>
    ```
    
    The file <task_definition_arn_definition.json> must comply with the following format:
    
    ```json
    {
        "taskDefinitionArn": "<task_definition_arn>"
    }
    ```

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
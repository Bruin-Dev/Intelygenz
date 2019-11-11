# ci-utils

In this folder are stored a series of scripts implemented in bash and python used as tools for the CI/CD process, these will be detailed in the sections shown below.

**Table of content:**

+ [Task_healtcheck](#task_healthcheck)
    - [Description](#task_healthcheck_description)
    - [Usage](#task_healthcheck_usage)
+ [Grafana_users_creation](#grafana_users_creation)
    - [Description](#grafana_users_creation_description)
    - [Usage](#grafana_users_creation_usage)
+ [Scripts utils delete_environments_aws_resources](#scripts_utils-delete_environments_aws_resources)
    - [Description](#delete_environments_aws_resources_description)

## Script task_healtheck<a name="task_healthcheck"></a>

### Description <a name="task_healthcheck_description"></a>

[This script](./task_healthcheck.sh) has been implemented in *shell scripting*, it is used to check if for a service of a given ECS cluster the last task definition relative to a service provided as parameter is being executed, as well as if it has a `HEALTHY` state.

This script loads the content of [another script](./common_functions.sh), where a series of util functions are declared being able to use them during its execution.

### Usage <a name="task_healthcheck_usage"></a>

To use this script it is necessary do the following:

* Declare previously the variable `TF_VAR_ENVIRONMENT` with the value of the ECS cluster on which you want to use it.
* Provide as parameter `-t` the name of the service on which you want to perform the check performed by the script explained above, as shown below:

    ```sh
    /bin/bash task_healthcheck.sh -t <service_name>
    ```

## Script grafana_users_creation<a name="grafana_users_creation"></a>

### Description <a name="grafana_users_creation_description"></a>

[This script](./grafana_users_creation.py) has been implemented in *Python*, it is used for the creation of users in the Grafana service running in a cluster of ECS provided relative to a previously deployed environment.

To create users, a series of https calls will be made to the endpoint exposed by the Route53 service of AWS for the backend service in the given environment.

### Usage <a name="grafana_users_creation_usage"></a>

To use this script it is necessary to declare a series of variables, exposed below:

* `ENVIRONMENT_SLUG`: Name of the branch relative to the environment where the script it's going to be used.

  >It is important to remember that for all environments other than production (`master` branch) it is necessary to apply the function `echo -n "<branch_name>" | sha256sum | cut -c1-8` on the branch name

* `GRAFANA_ADMIN_PASSWORD`: Password for the administrator user for the Grafana service related to the environment

* `GRAFANA_ADMIN_USER`: User name for the administrator user for the Grafana service related to the environment

* `GRAFANA_USER_EMAIL`: List of user emails separated by commas to use as an email field in the process of creating them in the Grafana service related to the environment

* `GRAFANA_USER_LOGIN`: List of user logins separated by commas to use as a login field in the process of creating them in the Grafana service related to the environment

* `GRAFANA_USER_NAME`: List of user names separated by commas to use as an user name field in the process of creating them in the Grafana service related to the environment

* `GRAFANA_USER_PASSWORD`: List of user password separated by commas to use as an user name field in the process of creating them in the Grafana service related to the environment

>The number of elements that must have the variables `GRAFANA_USER_EMAIL`, `GRAFANA_USER_LOGIN`, `GRAFANA_USER_NAME` and `GRAFANA_USER_PASSWORD` must be the same, since it is necessary to have all the fields related to the users to be created to be able to do it.

## Scripts utils delete_environments_aws_resources <a name="scripts_utils-delete_environments_aws_resources"></a>

### Description <a name="delete_environments_aws_resources_description"></a>

In the folder [`delete_environments_aws_resources`](./delete_environments_aws_resources) a series of *Python* files are stored, these allow the deletion of the resources created in AWS associated to an environment. The files mentioned are listed below:

* [`alb_py`](./delete_environments_aws_resources/alb_py): *Python* file where the class `ApplicationLoadBalancer` is implemented, in this one all the necessary functions to delete the Application Load Balancer associated to an environment are collected, as well as all the resources related to it (`TargetGroups`).

* [`ecs.py`](./delete_environments_aws_resources/ecs.py): *Python* file where the `EcsServices` class is implemented, in this one there are all the necessary functions to delete the ECS cluster associated to an environment, as well as all the resources related to it:
  
  * `ECS Services` defined in the cluster and `Tasks` of each one of them.
  
  * `Namespaces` and `Services` associated with the same to perform [*services discovery*](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-discovery.html) in the cluster

* [`metrics.py`](./delete_environments_aws_resources/metrics.py): *Python* file where the `Metrics` class is implemented, this one gathers the functions for the erasure of all the resources related to metrics for an environment:

  * `CloudWatch Alarms`
  
  * `CloudWatch Dashboard`

  * `CloudWatch Log Filters`

* [`redis.py`](./delete_environments_aws_resources/redis.py): *Python* file where the `RedisCluster` class is implemented, in charge of deleting and verifying the same of the ElatiCache Redis cluster associated to an environment.

* [`security_groups.py`](./delete_environments_aws_resources/security_groups.py): *Python* file where the `SecurityGroups` class is implemented, in this one the search and later erasure of all the security groups associated to the different resources created in *AWS* for an environment is carried out.

* [`main.py`](./delete_environments_aws_resources)
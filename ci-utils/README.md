# ci-utils

In this folder are stored a series of scripts in bash and python used as tools for the CI/CD process, these will be detailed in the sections shown below.

**Table of content:**

+ [task_healtcheck](task_healtcheck)
    - [Description](#task_healcheck_description)
    - [Usage](#task_healcheck_usage)

## Script task_healtheck<a name="task_healcheck"></a>

### Description <a name="task_healcheck_description"></a>
[This script](./task_healthcheck.sh) has been implemented in shell scripting, it is used to check if for a service of a given ECS cluster the last task definition relative to a service provided as parameter is being executed, as well as if it has a `HEALTHY` state.

This script loads the content of [another script](./common_functions.sh), where a series of functions are declared to print messages in log form, being able to use them to print messages in log form during its execution.

### Usage <a name="task_healcheck_usage"></a>

To use this script it is necessary do the following:

* Declare previously the variable `TF_VAR_ENVIRONMENT` with the value of the ECS cluster on which you want to use it.
* Provide as parameter `-t` the name of the service on which you want to perform the check performed by the script explained above, as shown below:
`/bin/bash task_healthcheck.sh -t <service_name>`
# Grafana

**Table of content:**

- [Dashboard_generator](#dashboard_generator)
    - [Description](#dashboard_generator_description)
    - [Usage](#dashboard_generator_usage)
- [Grafana_users_creation](#grafana_users_creation)
  - [Description](#grafana_users_creation_description)
  - [Usage](#grafana_users_creation_usae)

## Script dashboard_generator<a name="dashboard_generator"></a>

### Description <a name="dashboard_generator_description"></a>

[This script](./scripts/dashboard_generator.py) has been implemented in *Python* and it's used for the automatic generation of dashboards for some Mettel clients. It generates a folder for each provided company, creates a new dashboard with metrics for it and adds a new provider in the `dashboards/all.yaml` file to provisione it in Grafana.

### Usage <a name="dashboard_generator_usage"></a>

The script is automatically executed when a Docker image of Grafana is built.

## Script grafana_users_creation<a name="grafana_users_creation"></a>

### Description <a name="grafana_users_creation_description"></a>

[This script](./grafana_users_creation.py) has been implemented in *Python*, it is used for the creation of users in the Grafana service running in a cluster of ECS provided relative to a previously deployed environment. Apart from creating users, the script will assign each one different permissions based on Gitlab's environment variables.

To create users, a series of https calls will be made to the endpoint exposed by the Route53 service of AWS for the backend service in the given environment.

### Usage <a name="grafana_users_creation_usage"></a>

To use this script it is necessary to declare a series of variables, exposed below:

- `ENVIRONMENT_SLUG`: Name of the branch relative to the environment where the script it's going to be used.

  >It is important to remember that for all environments other than production (`master` branch) it is necessary to apply the function `echo -n "<branch_name>" | sha256sum | cut -c1-8` on the branch name

- `GRAFANA_ADMIN_PASSWORD`: Password for the administrator user for the Grafana service related to the environment

- `GRAFANA_ADMIN_USER`: User name for the administrator user for the Grafana service related to the environment

- `GRAFANA_USER_EMAIL`: List of user emails separated by commas to use as an email field in the process of creating them in the Grafana service related to the environment

- `GRAFANA_USER_LOGIN`: List of user logins separated by commas to use as a login field in the process of creating them in the Grafana service related to the environment

- `GRAFANA_USER_NAME`: List of user names separated by commas to use as a user name field in the process of creating them in the Grafana service related to the environment

- `GRAFANA_USER_PASSWORD`: List of user password separated by commas to use as a user password field in the process of creating them in the Grafana service related to the environment

- `GRAFANA_USER_ROLE`: List of user roles separated by commas to use as a user role field in the process of creating them in the Grafana service related to the environment. Valid values are `viewer`, `editor` and `admin`

- `GRAFANA_USER_COMPANY`: List of user companies separated by commas to use as a user company field in the process of creating them in the Grafana service related to the environment

>The number of elements that must have the variables `GRAFANA_USER_EMAIL`, `GRAFANA_USER_LOGIN`, `GRAFANA_USER_NAME`, `GRAFANA_USER_PASSWORD`, `GRAFANA_USER_ROLE` and `GRAFANA_USER_COMPANY` must be the same, since it is necessary to have all the fields related to the users to be created to be able to do it.

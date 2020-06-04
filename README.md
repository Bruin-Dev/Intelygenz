<div align="center">
<img src="https://media.licdn.com/dms/image/C4E0BAQHrME9aCW6ulg/company-logo_200_200/0?e=2159024400&v=beta&t=6xMNS1zK1F8asBlM16EzbJ4Im7SlQ8L7a7sgcaNzZQE"  width="200" height="200">
</div>

| Environment   | Status        |
|:-------------:|:-------------:|
| master        | [![pipeline status](https://gitlab.intelygenz.com/mettel/automation-engine/badges/master/pipeline.svg)](https://gitlab.intelygenz.com/mettel/automation-engine/commits/master) |

| Module      | Coverage |
|:-----------:|:--------:|
| bruin-bridge |[![bruin-bridge-test](https://gitlab.intelygenz.com/mettel/automation-engine/badges/master/coverage.svg?job=bruin-bridge-test)](https://gitlab.intelygenz.com/mettel/automation-engine/commits/master)
| cts-bridge |[![cts-bridge-test](https://gitlab.intelygenz.com/mettel/automation-engine/badges/master/coverage.svg?job=cts-bridge-test)](https://gitlab.intelygenz.com/mettel/automation-engine/commits/master)
| dispatch-portal-backend |[![dispatch-portal-backend-test](https://gitlab.intelygenz.com/mettel/automation-engine/badges/master/coverage.svg?job=dispatch-portal-backend-test)](https://gitlab.intelygenz.com/mettel/automation-engine/commits/master)
| last-contact-report |[![last-contact-report-test](https://gitlab.intelygenz.com/mettel/automation-engine/badges/master/coverage.svg?job=last-contact-report-test)](https://gitlab.intelygenz.com/mettel/automation-engine/commits/master)
| lit-bridge|[![lit-bridge-test](https://gitlab.intelygenz.com/mettel/automation-engine/badges/master/coverage.svg?job=lit-bridge-test)](https://gitlab.intelygenz.com/mettel/automation-engine/commits/master)
| lumin-billing-report|[![lumin-billing-report](https://gitlab.intelygenz.com/mettel/automation-engine/badges/master/coverage.svg?job=lumin-billing-report-test)](https://gitlab.intelygenz.com/mettel/automation-engine/commits/master)
| notifier|[![notifier-test](https://gitlab.intelygenz.com/mettel/automation-engine/badges/master/coverage.svg?job=notifier-test)](https://gitlab.intelygenz.com/mettel/automation-engine/commits/master)
| service-affecting-monitor|[![service-affecting-monitor-test](https://gitlab.intelygenz.com/mettel/automation-engine/badges/master/coverage.svg?job=service-affecting-monitor-test)](https://gitlab.intelygenz.com/mettel/automation-engine/commits/master)
| service-outage-monitor|[![service-outage-monitor-test](https://gitlab.intelygenz.com/mettel/automation-engine/badges/master/coverage.svg?job=service-outage-monitor-test)](https://gitlab.intelygenz.com/mettel/automation-engine/commits/master)
| sites-monitor|[![sites-monitor-test](https://gitlab.intelygenz.com/mettel/automation-engine/badges/master/coverage.svg?job=sites-monitor-test)](https://gitlab.intelygenz.com/mettel/automation-engine/commits/master)
| t7-bridge|[![t7-bridge-test](https://gitlab.intelygenz.com/mettel/automation-engine/badges/master/coverage.svg?job=t7-bridge-test)](https://gitlab.intelygenz.com/mettel/automation-engine/commits/master)
| tnba-monitor|[![tnba-monitor-test](https://gitlab.intelygenz.com/mettel/automation-engine/badges/master/coverage.svg?job=tnba-monitor-test)](https://gitlab.intelygenz.com/mettel/automation-engine/commits/master)
| velocloud-bridge|[![velocloud-bridge-test](https://gitlab.intelygenz.com/mettel/automation-engine/badges/master/coverage.svg?job=velocloud-bridge-test)](https://gitlab.intelygenz.com/mettel/automation-engine/commits/master)

# Table of Contents

- [Project structure](#project-structure)
  - [Naming conventions](#naming-conventions)
  - [Adding new microservice to the system](#adding-new-microservices-to-the-system)
- [Technologies used](#technologies-used)
- [Developing flow](#developing-flow)
  - [Deploying just a subset of microservices](#deploying-just-a-subset-of-microservices)
  - [DOD(Definition of Done)](#doddefinition-of-done)
  - [Custom packages](#custom-packages)
    - [Creation and testing](#creation-and-testing)
    - [Import and installation in microservices](#import-and-installation-in-microservices)
    - [Changes and debugging](#changes-and-debugging)
- [Running the project](#running-the-project)
  - [Python 3.6](#python-3.6)
  - [Docker and Docker Compose](#docker-and-docker-compose)
  - [Docker ECR private repository](#docker-ecr-private-repository)
  - [Docker custom images and python libraries](#docker-custom-images-and-python-libraries)
  - [Env files](#env-files)
  - [Finish up](#finish-up)
- [Lists of projects READMEs](#lists-of-projects-readmes)
  - [Packages](#packages)
  - [Microservices](#microservices)
  - [Acceptance Tests](#acceptance-tests)
- [Processes' overview](#processes-overview)
  - [Monitoring edge and link status](#monitoring-edge-and-link-status)
    - [Process goal](#process-goal)
    - [Process flow](#process-flow)
- [Good Practices](#good-practices)
- [METRICS](#metrics)

# Project structure

## Naming conventions

- For folders containing services: kebab-case
- For a python package(directory): all lowercase, without underscores
- For a python module(file): all lowercase, with underscores only if improves readability.
- For a python class: should use CapsWord convention.
- Virtual env folders should be `project-name-env`. In case it is in a custom package as a user test environment 
it should be `package-example-env`

From [PEP-0008](https://www.python.org/dev/peps/pep-0008/#package-and-module-names)
Also check this, more synthesized [Python naming conventions](https://visualgit.readthedocs.io/en/latest/pages/naming_convention.html) 

## Adding new microservices to the system
In addition to creating the microservice folder and all the standards files inside that folder, you must add this
new microservice and any new env variables to the system's files. This is done inorder to add 
it to both the infrastructure and the pipeline.
You will need to add/modify files in the folders of the 
- [automation-engine](#automation-engine),  
- [ci-utils](#ci-utils),
- [gitlab-ci](#gitlab-ci), 
- [infra-as-code](#infra-as-code), 
- and [installation-utils](#installation-utils)

Any new env variables should be added to the gitlab. And if there are two different var for PRO and DEV
specify it by appending `_PRO` or `_DEV` to the variable name on the gitlab.

### automation-engine
In the automation-engine folder you will need to update the:
- [.gitlab-ci.yml](.gitlab-ci.yml)
- [README.md](README.md)
- [docker-compose.yml](docker-compose.yml)

### ci-utils
In ci-utils you will need to makes changes to the following files:
-  [assign_docker_images_build_numbers.sh](ci-utils/assign_docker_images_build_numbers.sh) 
-  [manage_ecr_docker_images.py](ci-utils/manage_ecr_docker_images.py)

### gitlab-ci
If your microservices adds any new env variables you will need to make changes to the following file:
- [terraform-templates/.gitlab-ci-terraform-basic-templates.yml](gitlab-ci/terraform-templates/.gitlab-ci-terraform-basic-templates.yml)

### infra-as-code
In infra-as-code you will need to make the changes to the following locations:
- Add desired amount and any new env variables here: [.gitlab-ci.yml](infra-as-code/.gitlab-ci.yml)

- basic infra folder    
    - [ecr_repositories.tf](infra-as-code/basic-infra/ecr_repositories.tf)
- dev folder
    - Create a new file called `[new microservice name].tf`
    - If the microservice is a capability then it goes in the `depends_on` sections of the use cases' terraform file
    - [locals.tf](infra-as-code/dev/locals.tf)
    - [metrics-prometheus.tf](infra-as-code/dev/metrics-prometheus.tf)
    - In [variable.tf](infra-as-code/dev/variables.tf) Copy the other services' variable `[microservice name]_BUILD_NUMBER` 
      for the new microservice and swap the name. Also copy the format for the desired amount and make one for the new service.
      Any new env variables will be placed here as well.
    - dashboard-definitions folder
        -   [dashboard_cluster_definition.json](infra-as-code/dev/dashboards-definitions/dashboard_cluster_definition.json)
    - task-definitions folder
        -   Create a new file called `[new microservice name].json`
 
### installation-utils
In installation-utils you will need to make changes to the following files:
- [environment_files_generator.py](installation-utils/environment_files_generator.py)

# Technologies used

- [Python 3.6](https://www.python.org/downloads/release/python-360/)
- [Python asyncio](https://docs.python.org/3/library/asyncio.html)
- [Quart](http://pgjones.gitlab.io/quart/)
- [Quart OpenAPI](https://github.com/factset/quart-openapi)
- [Pytest](https://docs.pytest.org/en/latest/)
- [Behave](https://pypi.org/project/behave/)
- [Pip](https://pypi.org/project/pip/)
- [Virtualenv](https://virtualenv.pypa.io/en/latest/)
- [Hypercorn to deploy Quart server](https://pgjones.gitlab.io/hypercorn/)
- [Requests for python HTTP requests](http://docs.python-requests.org/en/master/)
- [NATS (as event bus)](https://github.com/nats-io/nats-server)
- [Docker](https://www.docker.com/)
- [Docker-compose](https://docs.docker.com/compose/)
- [markdown-toc (for Table of Contents generation in READMEs)](https://github.com/jonschlinkert/markdown-toc)
- [PEP8 pre-commit hook](https://github.com/cbrueffer/pep8-git-hook) **MANDATORY**
- [AWS Fargate](https://aws.amazon.com/fargate/)

# Developing flow

- Create a branch from development
  
  - "feature" branches starts with `feature/<feature-name>` or `dev/feature/<feature-name>`
  - "fix" branches starts with `fix/<issue-name>` or `dev/fix/<issue-name>`

  Branches whose name begins with `dev/feature/<feature-name>` or `dev/fix/issue-name` will perform both [CI](docs/PIPELINES.md#continuous-integration-ci) and [CD](docs/PIPELINES.md#continuous-delivery-cd) processing, while those whose name begins with `feature-<feature-name>` or `fix-<issue-name>` will perform only [CI](docs/PIPELINES.md#continuous-integration-ci) processing.

  >It is strongly recommended to always start with a `feature/<feature-name>` or `fix/<issue-name>` branch, and once the development is ready, rename it to `dev/feature/<feature-name>` or `dev/fix/<issue-name>` and push this changes to the repository.

- When taking a fix or a feature, create a new branch. After first push to the remote repository, start a Merge Request with the title like the following: "WIP: your title goes here". That way, Maintainer and Approvers can read your changes while you develop them.
- **Remember that all code must have automated tests(unit and integration and must be part of an acceptance test) in it's pipeline.** 
- Assign that merge request to a any developer of the repository. Also add any affected developer as Approver. I.E: if you are developing a microservice wich is part of a process, you should add as Approvers both the developers of the first microservice ahead and the first behind in the process chain. Those microservices will be the more affected by your changes. 
- When a branch is merged into master, it will be deployed in production environment.
- When a new branch is created, it will be deployed in a new Fargate cluster. When a branch is deleted that cluster is deleted. **So every merge request should have "delete branch after merge"**
- You can also check in gitlab's project view, inside Operations>Environments, to see current running environments

## Deploying just a subset of microservices

Due to the limited number of task instances available per account in AWS (50 instances at the time of this writing), it is highly recommended that developers configure just the tasks they need to use for their deployments so ephemeral environments do not consume more AWS resources (task instances) than needed. To do so, they must perform the following steps:

1. There are two jobs defined in the `infra-as-code/.gitlab-ci.yml` file: `deploy-branches` and `check-ecs-resources-branches`. A set of variables are used within them to configure the number of tasks per microservice. The naming of these variables follows the convention `<service_name>_desired_tasks`, where `service_name` is the name of the microservice declared in AWS. These variables are declared in the global variables section of the `.gitlab-ci.yml` file in the repository root.
    > If the variable is set to 0, no tasks instances will be created for that microservice. The corresponding service won't be created at ECS either.

2. If the developer has doubts about what microservices should be taken into account for an ephemeral environment, they should take a look at the README file of that microservice. After guessing that, the corresponding `<service_name>_desired_tasks` must be set with a minimal value of 1 in order to get the task instances created when the deployment finishes.

3. Once the development has finished, the value of `<service_name>_desired_tasks` variables that were modified must be reverted to the value they hold in the `master` branch.

The following example shows how to configure `<service_name>_desired_tasks` variables strictly needed to have the `service-affecting-monitor` microservice working in an ephemeral environment, including microservices it depends on.

```sh
variables:
  . . .
  bruin_bridge_desired_tasks: 0
  dispatch_portal_backend_desired_tasks: 1
  last_contact_report_desired_tasks: 1
  lit_bridge_desired_tasks: 1
  metrics_prometheus_desired_tasks: 0
  nats_server_desired_tasks: 0
  nats_server_1_desired_tasks: 1
  nats_server_2_desired_tasks: 1
  notifier_desired_tasks: 1
  service_affecting_monitor_desired_tasks: 1
  service_outage_monitor_1_desired_tasks: 0
  service_outage_monitor_2_desired_tasks: 0
  service_outage_monitor_3_desired_tasks: 0
  service_outage_monitor_4_desired_tasks: 0
  service_outage_monitor_triage_desired_tasks: 0
  sites_monitor_desired_tasks: 0
  t7_bridge_desired_tasks: 0
  velocloud_bridge_desired_tasks: 5
  . . .
```

## DOD(Definition of Done)

If any of the next requirements is not fulfilled in a merge request, merge request can't be merged. 

- Each service must have unit tests with a coverage percent of the 80% or more.
- Each service must have it's dockerfile and must be referenced in the docker-compose.
- Each service must have a linter job and a unit tests job in the gitlab.ci pipeline.
- If it is a new service, all the terraform code to deploy it should be present.
- Developers should take care of notify the devops/tech lead of putting in the pipeline env any environment variable needed in the pipeline's execution.

# Running the project

This tutorial assumes Ubuntu 18.04 - it might work in other versions of Ubuntu though, but hasn't been tested.

## Python 3.6

Open a terminal and run:

`$ python3 -V`

Python 3.6 is pre-installed in Ubuntu 18.04 so the output should be something like:

`Python 3.6.8`

## Docker and Docker Compose

Remove any old versions and install the latest one:

```bash
$ apt update -y
$ apt -y upgrade
$ apt remove docker docker-engine docker.io
$ apt install docker.io
```

For Docker Compose there's a good tutorial in [the official docs](https://docs.docker.com/compose/install/). Summarizing it says:

```bash
$ curl -L "https://github.com/docker/compose/releases/download/1.24.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
$ chmod +x /usr/local/bin/docker-compose
$ docker-compose --version
```

Last command should output something like:

`docker-compose version 1.24.1, build 4667896b`

## Docker ECR private repository

For the images of the Python microservices, one of the custom images uploaded to the ECR repository used in the project is used as a base, these are generated from a [specific repository](https://gitlab.intelygenz.com/mettel/docker_images) for this purpose.

In order to use these images it will be necessary to have configured the authentication with this private repository. To do this it is necessary to perform the following steps:

1. Install awscli, executing from a terminal the following command

    ```bash
    $ sudo pip3 install awscli -U
    ```

2. Set up a specific profile with the user's credentials in the AWS account used in the project. To do this, if the `~/.aws/credentials` file does not exist, it will be necessary to modify or create it and add the following

   ```bash
   [mettel-automation]
   aws_access_key_id = <user_aws_access_key_id>
   aws_secret_access_key = <user_secret_access_key>
   ```

3. Configure the profile created in the previous step, to do this it is necessary to modify or create in case there is no `~/.aws/config` and add the following:

   ```bash
   [profile mettel-automation]
   region=us-east-1
   output=json
   ```

4. Use the awscli tool to generate a new entry in `~/.docker/config.json` with the necessary credentials for the ECR repository used in the repository. To do this you need to run the following command:

   ```bash
   $(aws ecr get-login --no-include-email --profile mettel-automation)
   ```

   The above command creates a temporary token in the `~/.docker/config.json` file, so it is possible that after a while an error like the one below will occur when trying to access the ECR repository:

    ```bash
    ERROR: Service 'last-contact-report' failed to build: pull access denied for 374050862540.dkr.ecr.us-east-1.amazonaws.com/automation-python-3.6, repository does not exist or may require 'docker login': denied: Your Authorization Token has expired. Please run 'aws ecr get-login --no-include-email' to fetch a new one.
    ```

   To solve this error, simply execute the command mentioned in this step for the generation of a new token.

## Docker custom images and Python Libraries

As mentioned in the previous section, the project uses custom images created from a specific repository, in which semantic-release is used to version these images. Each of these images has a specific version of the python library `igzpackages` installed.

There are a number of variables to indicate the version number of these images, as well as of the `igzpackages` library, which will be used in the CI/CD process of the branch you are working on

- `IGZ_PACKAGES_VERSION`: Used version of the `igzpackages` library. These are published in a S3 bucket, accessible via [CloudFront URL](https://s3pypi.mettel-automation.net/igzpackages/index.html).

- `DOCKER_BASE_IMAGE_VERSION`: Used version of the docker custom images as base images of the Python microservices in its `Dockerfile`.

>The versions are available in the [releases](https://gitlab.intelygenz.com/mettel/docker_images/-/releases) section of the repository that manages igzpackages.

These variables are indicated in different ways, depending on whether you want to make the changes locally or in an AWS environment:

- For deploy in an AWS environment it's necessary modify the [.gitlab-ci.yml](.gitlab-ci.yml) file, as explained below:

  ```yaml
  . . .

  variables:
    . . .
    IGZ_PACKAGES_VERSION: 1.0.9
    DOCKER_BASE_IMAGE_VERSION: 1.0.7
    . . .

  . . .
  ```

  So in case you want to change the version used of the `igzpackages` library and/or the base docker images you must change the variables mentioned. These changes will affect the construction of the different images of the microservices to be deployed in AWS or in local environment.

- For the local environment, two files must be modified:

  - In the different microservices declared in the [docker-compose.yml](./docker-compose.yml) file for local use, you must change the version of the docker images to be used, **so it is important to update them with the desired values, below you can see how they are used in this file for a microservice declaration**

    ```yaml
      <microservice_name>:
        build:
          context: .
          dockerfile: <microservice_folder>/Dockerfile
          args:
            DOCKER_BASE_IMAGE_VERSION: 1.0.7
      . . .
    ```

  - In each of the `requirements.txt` files of the microservices, which allow these libraries to be installed in the local environment, indicating `-f` flag so that these libraries are searched in the URL configured by means of Cloudfront to access the index.html where the different versions are located. Below is an example of this file for the `velocloud-bridge` microservice

    ```bash
    . . .
    -f https://s3pypi.mettel-automation.net/igzpackages/index.html
    igzpackages==2.0.0
    ```

>It is important to reflect the changes in all files simultaneously so that the version of the development in local and AWS is the same at the end of the development of a feature or fix.

## Env files

Ask a maintainer for a temp private token. Clone the mettel repo and run:

```bash
$ cd installation-utils
$ python3 -m pip install -r requirements.txt
$ python3 environment_files_generator.py <private_token>
```

That'll generate all env files needed.

## Finish up

Run:

`$ docker-compose up --build`

# Lists of projects READMEs

## Microservices

- [Base microservice](base-microservice/README.md)
- [Sites monitor](sites-monitor/README.md)
- [TNBA monitor](tnba-monitor/README.md)
- [Velocloud bridge](velocloud-bridge/README.md)
- [Notifier](notifier/README.md)

## Acceptance Tests

- [Acceptance tests](acceptance-tests/README.md)

# Processes' overview

## Monitoring edge and link status

Services involved: sites-monitor, velocloud-bridge, notifier.

### Process goal

- Given an interval, process all edges and links statuses in that interval.
- Notify in a given channel. Just notify the faulty edges and a metric of it's statuses.

### Process flow

- Sites Monitor send a message to the Bridge through to ask for all edges given a list of Velocloud clusters.
- For each edge it builds an event composed by the cluster's hostname, the edge ID and the company ID for that edge.
- Publish events on NATS.
- Sites Monitor consumes the events from NATS and then send each edge to the NATS to be consumed by the Bridge.
- For each event, it fetches the edge and link data related to the given IDs
- Publishes edge and link data to NATS
- Depending on the state of the edge, the Sites Monitor will put the result event in a different Message Queue (one Queue for faulty edges, other for ok edges)
- Notifier consumes the faulty edge queue and creates statistics. 
- Notifier has an interval set. For each interval will send the statistics to a Slack channel and reset the statistics for the next cycle.

# Good Practices

- Documentation **must** be updated as frecuently as possible. It's recomended to annotate every action taken in the development phase, and afterwards, add to the documentation the actions or information considered relevant.
- Pair programming is strongly reccomended when doing difficult or delicate tasks. It is **mandatory** when a new teammate arrives.
- Solutions of hard problems should be put in common in order to use all the knowledge and points of view of the team.

# METRICS

- [Prometheus](http://localhost:9090) 
  - Github [link](https://github.com/prometheus/client_python) to documentation of Prometheus
  
  - Prometheus allows us to create counters/gauges in the velocloud-bridge to keep track of the metrics
    about edges processed in the bridge, amount of certain edges states found in the bridge, and amount of certain link states found in the bridge.
  
  - Using prometheus `start_http_server` we can host our metrics on a server. By using the file `prometheus.yml`located at
`/metrics-dashboard/prometheus/` and using the format below, you can add your server to the prometheus app. All the servers connected
to the prometheus app can be found at `http://localhost:9090/targets`.

    ```bash
    - job_name: <the microservice thats hosting you server>
      scrape_interval: 5s
      static_configs:
      - targets: [' <the microservice thats hosting you server>:<that server's port>']
    ```

- [Grafana](http://localhost:3000) admin/password

  - Grafana allows us to create graphs, tables, charts, and etc with the metrics created using Prometheus and other 
    default metrics.
  - [Link](https://prometheus.io/docs/prometheus/latest/querying/functions/) to functions you can use with your 
    Prometheus metrics in Grafana. 
  - You can run the Grafana server at `http://localhost:3000` using the credentials above.
  - In Grafana you can export a dashboard as a json file. By going to `metrics-dashboard/grafana/dashboard-definitions`
    you can add that json file to that folder and whenever the Grafana app is loaded up you can choose to make a new
    dashboard or use the dashboard that you created.  
  - [Link](https://grafana.com/docs/reference/dashboard/) to the documentation to the dashboard's json file.
  - The docker_compose should include the credentials above,specifically the password, in the`GF_SECURITY_ADMIN_PASSWORD` 
    area for the [local docker-compose](docker-compose.yml). Also the `GF_INSTALL_PLUGINS` field can be used to add any plugins you want to add to the
    grafana dashboard.


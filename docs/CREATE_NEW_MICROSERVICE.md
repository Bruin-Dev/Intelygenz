<div align="center">
<img src="https://media.licdn.com/dms/image/C4E0BAQHrME9aCW6ulg/company-logo_200_200/0?e=2159024400&v=beta&t=6xMNS1zK1F8asBlM16EzbJ4Im7SlQ8L7a7sgcaNzZQE"  width="200" height="200">
</div>

# CREATE NEW MICROSERVICE

 > This process describes step by step how to create a new microservice, from the ECR repository to the helm chart templates that 
 > define the microservice. All of this is created from the Gitlab repository in the pipeline; no need for more tools or actions 
 > by the developer. 

## Introduction

The process requires that the steps be carried out in order. Basically, it is necessary to create the ECR repository
first so that we can then start developing and testing our new microservice in ephemeral environments or in production.

## 1. Create ECR repository

We can't create the ECR repository in the branch where we are developing because the creation or update of the ECR repositories 
is only in the Master branch. This means that the first thing that we need to do is make a little merge to master to create our 
new microservice repo, by that way we can deploy our microservice later in dev branches.

  * create a new branch from master
  * create a new terraform ECR repo file in the folder: `infra-as-code/ecr-repositories` you can copy any of the other repos to have an example.
    * this is an example:
    ````bash
    resource "aws_ecr_repository" "new-microservice-repository" {
    name = "new-microservice"
    tags = {
        Project       = var.common_info.project
        Provisioning  = var.common_info.provisioning
        Module        = "new-microservice"
    }
    }
    ````
  * merge the new repository to Master branch. The pipeline will run and create the new ECR repo.

## 2. Create our new microservice

We can start working on our new microservice based on an existing one. It depends if is a `capability`(bridges) or a `use case`. Select one or other depends on what are you developing. For example let's copy a capability "bruing-bridge" and paste in the root of the repo to change his name to "new-bridge". from this moment you can start to develop and do your tests locally. Every microservice must have the following directory structure:

````
new-bridge
├── .gitlab-ci.yml
├── Dockerfile
├── README.md
├── package.json
├── requirements.txt
├── setup.py
└── src
    ├── app.py
    ├── application
    │   └── ...
    ├── config
    │   └── ...
    └── tests
        └── ...
````

## 3. Update CI-CD gitlab files with the proper values

It's important to have the .gitlab-ci.yaml files correctly defined to enable pipelines:
  * `new-bridge/.gitlab-ci.yml`
  Change any reference to de template microservice to the new one.. example find and replace "bruin-bridge" for "new-bridge"
  * `.gitlab-ci.yml` (the file in the root of the repository)
  Here we need to specify to gitlab-ci that we define other jobs in a different directories (the .gitlab-ci.yml of our new repo). So locate the root gitlab file and add a new line with the path of the new micro jobs (do it respecting the alphabetical order)
````
...
  - local: 'links-metrics-api/.gitlab-ci.yml'
  - local: 'links-metrics-collector/.gitlab-ci.yml'
  - local: 'lumin-billing-report/.gitlab-ci.yml'
  - local: 'new-bridge/.gitlab-ci.yml'    <─────────────── here!
  - local: 'notifier/.gitlab-ci.yml'
  - local: 'service-affecting-monitor/.gitlab-ci.yml'
  - local: 'service-outage-monitor/.gitlab-ci.yml'
...
````
  Now in the same file, let's define the "desired_tast" variable for this new micro (do it respecting the alphabetical order):
````
...
  NATS_SERVER_DESIRED_TASKS: "1"
  NATS_SERVER_1_DESIRED_TASKS: "1"
  NATS_SERVER_2_DESIRED_TASKS: "1"
  NEW_BRIDGE_DESIRED_TASKS: "1"    <─────────────── here!
  NOTIFIER_DESIRED_TASKS: "1"
  SERVICE_AFFECTING_MONITOR_DESIRED_TASKS: "1"
  SERVICE_OUTAGE_MONITOR_1_DESIRED_TASKS: "1"
...
````

## 3. Configure semantic-release 

We need to edit two files, one in the new micro path and other in the root of the repo:
  * `new-bridge/package.json`
  update the name of the micro with our new working name (do it respecting the alphabetical order):
````
{
    "name": "new-bridge",    <─────────────── here!
    "version": "0.0.1",
    "dependencies": {},
    "devDependencies": {}
}
````
  * `package.json` (the file in the root of the repository)
  add to the semantic-release global config our new path to analize version changes (do it respecting the alphabetical order):
````
...
    "./links-metrics-api",
    "./links-metrics-collector",
    "./lumin-billing-report",
    "./new-bridge",    <─────────────── here!
    "./notifier",
    "./service-affecting-monitor",
    "./service-outage-monitor",
...
````

## 3. Configure logs

We use 2 systems to storage logs, papertrail for 3 days and cloudwath for 1 month. Let's add those config in:
  * `ci-utils/papertrail-provisioning/config.py`
  just copy one block form other microservice and paste with the name of our new micro (do it respecting the alphabetical order):
````
...
                {
                    "query": f"lumin-billing-report AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[lumin-billing-report] - logs",
                    "repository": "lumin-billing-report",
                },
                {                                                                       ¯│
                    "query": f"new-bridge AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",    │
                    "search_name": f"[new-bridge] - logs",                               ├──────────────> here!
                    "repository": "new-bridge",                                          │
                },                                                                      _│
                {
                    "query": f"notifier AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[notifier] - logs",
                    "repository": "notifier",
                },
...
````

  * `helm/charts/fluent-bit-custom/templates/configmap.yaml`
  The same; copy one block form other microservice and paste with the name of our new micro (do it respecting the alphabetical order):
````
...
    [OUTPUT]
        Name                cloudwatch
        Match               kube.var.log.containers.lumin-billing-report*
        region              {{ .Values.config.region }}
        log_group_name      {{ .Values.config.logGroupName }}
        log_stream_name     lumin-billing-report
        auto_create_group   true
    [OUTPUT]                                                      ¯│
        Name                cloudwatch                             │
        Match               kube.var.log.containers.new-bridge*    │
        region              {{ .Values.config.region }}            ├──────────────> here!
        log_group_name      {{ .Values.config.logGroupName }}      │
        log_stream_name     new-bridge                             │
        auto_create_group   true                                  _│
    [OUTPUT]
        Name                cloudwatch
        Match               kube.var.log.containers.notifier*
        region              {{ .Values.config.region }}
        log_group_name      {{ .Values.config.logGroupName }}
        log_stream_name     notifier
        auto_create_group   true
...
````


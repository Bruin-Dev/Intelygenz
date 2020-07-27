<div align="center">
<img src="https://media.licdn.com/dms/image/C4E0BAQHrME9aCW6ulg/company-logo_200_200/0?e=2159024400&v=beta&t=6xMNS1zK1F8asBlM16EzbJ4Im7SlQ8L7a7sgcaNzZQE"  width="200" height="200">
</div>

# Pipelines

In this project is implemented Software delivery with total automation, thus avoiding manual intervention and therefore human errors in our product.

Human error can and does occur when carrying out these boring and repetitive tasks manually and ultimately does affect the ability to meet deliverables.

All of the automation is made with Gitlab CI technology, taking advantage of all the tools that Gitlab has.
We separate the automatation in two parts, [continuous integration](#continuous-integration-ci) and [continuous delivery](#continuous-delivery-cd), that are explained in the next sections.

To improve the speed and optimization of the pipelines, **only the jobs and stages will be executed on those modules that change in each commit**. 

**Exceptionally, it is possible to launch a pipeline with all the jobs and stages on a branch using the web interface, as shown in the following image**. To do so, the following steps must be followed:

   1. From the project repository select the `CI/CD` option in the left sidebar and this `Pipelines`, as shown in the following image where these options are marked in red.
   ![IMAGE: Select_CI_option](./img/pipelines/Select_CI_option.png)
   
   2. Choose the `Run Pipeline` option, as shown in the image below in red.
   ![IMAGE: select_run_pipeline](./img/pipelines/select_run_pipeline.png)
   
   3. Indicate the branch where you want to run the pipeline in the `Run for` box and then click on `Run pipeline`. It's possible see an example in the following image, where the box `Run for` is shown in green and `Run pipeline` is shown in red.
   ![IMAGE: select_run_pipeline_branch](./img/pipelines/select_run_pipeline_branch.png)

# Environments

In the project there are two types of environments in the project:

* **Production**: The environment is related to everything currently running in AWS related to the latest version of the `master` branch of the repository.

* **Ephemerals**: These environments are created from branches that start with name `dev/feature` or `dev/fix`.

>The name of any environment, regardless of the type, will identify all the resources created in the deployment process. The names for environments are `automation-master` for production, as well as `automation-<branch_identifier>` for ephemeral environments, being `branch_identifier` the result of applying `echo -n "<branch_name>" | sha256sum | cut -c1-8` on the branch name related to the ephemeral environment. These names will identify all the resources created in AWS during the [continuous delivery](#continuous-delivery-cd) process, explained in the following sections.

# Continuous integration (CI)

> Continuous Integration (CI) is a development practice where developers integrate code into a shared repository frequently, preferably several times a day. Each integration can then be verified by an automated build and automated tests. While automated testing is not strictly part of CI it is typically implied.
> [Codeship](https://codeship.com/continuous-integration-essentials)

![IMAGE: CI_MetTel_Automation.png](./img/pipelines/CI_MetTel_Automation.png)

## Validation steps

This stage checks the following:

* All python microservices comply with the rules of [PEP8](https://www.python.org/dev/peps/pep-0008/#package-and-module-names)

* Terraform files used to configure the infrastructure are valid from a syntactic point of view.

* The frontend modules comply with the linter configured for them

## Unit tests steps

All the available unit tests for each service should be run in this stage of the CI process.

If the coverage obtained from these tests for a service is not greater than or equal to 80%, it will cause this phase to fail, this will mean that the steps of the next stage will not be executed and the process will fail.

In cases in which a module does not reach the minimum coverage mentioned above, a message like the following will be seen in the step executed for that module.

![IMAGE: unit_test_coverage_not_reach_minimum.png](./img/pipelines/unit_test_coverage_not_reach_minimum.png)

# Continuous delivery (CD)

> Continuous deployment is the next step of continuous delivery: Every change that passes the automated tests is deployed to production automatically. Continuous deployment should be the goal of most companies that are not constrained by regulatory or other requirements.
> [Puppet.com](https://puppet.com/blog/continuous-delivery-vs-continuous-deployment-what-s-diff)

![IMAGE: CD_MetTel_Automation.png](./img/pipelines/CD_MetTel_Automation.png)

## Basic_infra steps

This area covers the checking and creation, if necessary, of all the basic resources for the subsequent deployment, these being the specific image repositories in [ECR Docker Container Registry](https://aws.amazon.com/ecr), as well as the roles necessary in AWS to be able to display these images in [ECS Container Orchestrator](https://aws.amazon.com/ecs/).

In this stage is also checked whether there are enough free resources in ECS to carry out the deployment with success or not.

## Build steps

This area will cover all build steps of all necessary modules to deploy the app to the selected environment. It's typical to build the docker images and push to the repository in this step.

## Deploy steps

In these works  *MetTel Automation* modules in the monorepo will be deployed to the selected environment, as well as all the resources associated to that environment in AWS.

In these jobs services in the monorepo will be deployed to the selected environment. The deploy steps will deploy the following in AWS:

* An [ECS Cluster](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ECS_clusters.html) will be created for the environment with a set of resources

  * An [ECS Service](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs_services.html) that will use the new Docker image uploaded for each service of the project, being these services the specified below:

    * [bruin-bridge](../bruin-bridge)
    
    * [cts-bridge](../cts-bridge)
    
    * [dispatch-portal-backend](../dispatch-portal-backend)
    
    * [dispatch-portal-frontend](../dispatch-portal-frontend)

    * [last-contact-report](../last-contact-report)
    
    * [lit-bridge](../lit-bridge)
    
    * [lumin-billing-report](../lumin-billing-report)

    * [metrics-prometheus](../metrics-dashboard/grafana)

    * [nats-server, nats-server-1, nats-server-2](../nats-server)

    * [notifier](../notifier)

    * [service-affecting-monitor](../service-affecting-monitor)
    
    * [service-dispatch-monitor](../service-dispatch-monitor)

    * [service-outage-monitor-1, service-outage-monitor-2, service-outage-monitor-3, service-outage-monitor-4, service-outage-monitor-triage](../service-outage-monitor)
    
    * [sites-monitor](../sites-monitor)

    * [t7-bridge](../t7-bridge)

    * [tnba-monitor](../tnba-monitor)

    * [velocloud-bridge](../velocloud-bridge)

  * A [Task Definition](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/example_task_definitions.html) for each of the above *ECS Services*

In this process, a series of resources will also be created in AWS for the selected environment, as follows:

* An [ElastiCache Redis Cluster](https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/WhatIs.html)

* An [ALB](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/introduction.html)

* A [record](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/rrsets-working-with.html) in [Route53](https://aws.amazon.com/route53/features/)

* A [CloudWatch Log Group](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/CloudWatchLogsConcepts.html)

* An [Service Discovery Service](https://aws.amazon.com/blogs/aws/amazon-ecs-service-discovery/) for each ECS Service of the ECS Cluster created for this environment and a [Service Discovery Namespace](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-discovery.html) to logically group these *Service Discovery Services*.

* A set of resources related to the metrics of the environment:

  * [CloudWatch Alarms](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html)

  * [CloudWatch Dashboard](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Dashboards.html)

  * [CloudWatch Log Filters](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/FilterAndPatternSyntax.html)

* A [CloudFormation Stack](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/stacks.html) for create the [SNS topic](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sns-topic.html) that will be used by *CloudWatch Alarms* notifications of this environment

* A [S3 bucket](https://docs.aws.amazon.com/AmazonS3/latest/gsg/GetStartedWithS3.html) to store the content of the metrics obtained by [Thanos](https://thanos.io/) and displayed through [Grafana](https://grafana.com/).

Also, resources of type [null_resource](https://www.terraform.io/docs/providers/null/resource.html) are created to execute some Python scripts:

1. The creation of [ECS Services](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs_services.html) starts only if a Python script launched as a `null_resource` finishes with success. 

    This script checks that the last ECS service created for NATS is running in `HEALTHY` state.

2. If the previous step succeeded then ECS services related to capabilities microservices are created, with these being the following:

    - `bruin-bridge`
    - `cts-bridge`
    - `lit-bridge`
    - `notifier`
    - `prometheus`
    - `t7-bridge`
    - `velocloud-bridge` 

    Once created, the script used for NATS is launched through `null_resource` to check that the task instances for each of these ECS services were created successfully and are in `RUNNING` and `HEALTHY` status.

3. Once all the scripts for the capabilities microservices have finished successfully, ECS services for the use-cases microservices are all created, with these being the following:
    
    - `dispatch-portal-backend`
	- `last-contact-report`
	- `lumin-billing-report`
	- `service-affecting-monitor`
	- `service-dispatch-monitor`
	- `service-outage-monitor-1`
	- `service-outage-monitor-2`
	- `service-outage-monitor-3`
	- `service-outage-monitor-4`
	- `service-outage-monitor-triage`
	- `sites-monitor`
	- `tnba-monitor`

   This is achieved by defining explicit dependencies between the ECS services for the capabilities microservices and the set of null resources that perform the healthcheck of the capabilities microservices.​

   The following is an example of a definition for the use-case microservice `service-affecting-monitor` using [*Terraform*](https://www.terraform.io/). Here, the dependency between the corresponding `null_resource` type resources in charge of performing the health check of the different capabilities microservices in Terraform code for this microservice is established.

   ```terraform
   resource "aws_ecs_service" "automation-service-affecting-monitor" {

      . . .

        depends_on = [ null_resource.bruin-bridge-healthcheck,
                       null_resource.cts-bridge-healthcheck,
                       null_resource.lit-bridge-healthcheck,
                       null_resource.velocloud-bridge-healthcheck,
                       null_resource.t7-bridge-healthcheck,
                       null_resource.notifier-healthcheck,
                       null_resource.metrics-prometheus-healthcheck ]
      . . .
   }
   ```

   >This procedure has been done to ensure that use case microservices are not created in ECS until new versions of the capability-type microservices are properly deployed, as use case microservices need to use capability-type microservices.

4. The provisioning of the different groups and the searches included in each one of them is done through a [python utility](../ci-utils/papertrail-provisioning), this makes calls to the util [go-papertrail-cli](https://github.com/xoanmm/go-papertrail-cli) who is in charge of the provisioning of the elements mentioned in [Papertrail](https://papertrailapp.com/).
---
With passion from the [Intelygenz](https://www.intelygenz.com) Team @ 2020
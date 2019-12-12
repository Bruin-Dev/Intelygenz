<div align="center">
<img src="https://media.licdn.com/dms/image/C4E0BAQHrME9aCW6ulg/company-logo_200_200/0?e=2159024400&v=beta&t=6xMNS1zK1F8asBlM16EzbJ4Im7SlQ8L7a7sgcaNzZQE"  width="200" height="200">
</div>

# INFRASTRUCTURE AS CODE

 > Infrastructure as Code (IaC) is the management of infrastructure (networks, virtual machines, load balancers, 
 > and connection topology) in a descriptive model, using the same versioning as DevOps team uses for source code. 
 > Like the principle that the same source code generates the same binary, an IaC model generates the same environment 
 > every time it is applied. IaC is a key DevOps practice and is used in conjunction with continuous delivery.
 > [Azure](https://docs.microsoft.com/en-us/azure/devops/learn/what-is-infrastructure-as-code)

## Introduction

Infrastructure as Code enables DevOps to test the deployment of environments before use it in production. IaC can deliver 
stable environments rapidly and at scale. Avoiding manual configuration of environments and enforce consistency by representing
 the desired state of their environments via code. This technique improve the automatic deployments in Nextinit, each time 
 the pipelines launch the [Continuous delivery](./PIPELINES.md##continuous-delivery-cd) will create, update or destroy 
 the infrastructure if it's necessary. 

## IaC in MetTel Automation

Nextinit runs IaC with [terraform](https://www.terraform.io/), this task is/will be included in the automation [pipelines](./PIPELINES.md##Pipelines).
Terraform save the state of the infrastructure in a storage, these files have the extension **.tfstate**. In MetTel Automation we
saves these files in a protected Cloud storage to centralize the states and be accessible each time the pipeline needs to deploy/update
the infrastructure.

## Folder structure

````
infra-as-code/
├── basic-infra             # basic infrastructure in AWS
└── dev                     # AWS resources for each environment (ECS Cluster, ElastiCache Cluster, etc.)
└── network-resources       # network resources infrastructure in AWS
````

Al terraform files are located inside `./infra-as-code`, in this folder there are four additional folders, `basic-infra`, `dev`, `ecs-services` and `network-resources`.

1. `basic-infra`: there are the necessary terraform files to create the Docker images repositories in ECS, and the roles and policies necessary for use these.

2. `dev`: there are the necessary terraform files for create the resources used for each environment in AWS, these are as follows

    * An [ECS Cluster](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ECS_clusters.html), the [ECS Services](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs_services.html) and its [Task Definition](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/example_task_definitions.html) for all the microservices present in the project

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

    * A set of [Security Groups](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-security-groups.html) for all the resources created by the terraform files present in this folder

3. `network-resources`: there are the necessary files for create the [VPC](https://aws.amazon.com/vpc/) and all related resources in the environment used for deployment, these being the following:

    * [Internet Gateway](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Internet_Gateway.html)

    * [Elastic IP Addresses](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/elastic-ip-addresses-eip.html)

    * [NAT Gateways](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-nat-gateway.html)

    * [Subnets](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Subnets.html)

    * [Route tables](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Route_Tables.html) for the created subnets

    * A set of [Security Groups](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-security-groups.html) for all the resources created by the terraform files present in this folder
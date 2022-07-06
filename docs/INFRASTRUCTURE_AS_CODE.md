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
 the desired state of their environments via code. This technique improves the automatic deployments in automation-engine, each time 
 the pipelines launch the [Continuous delivery](./PIPELINES.md##continuous-delivery-cd) will create, update or destroy 
 the infrastructure if it's necessary. 

## IaC in MetTel Automation

Automation-engine runs IaC with [terraform](https://www.terraform.io/), this task is/will be included in the automation [pipelines](./PIPELINES.md##Pipelines).
Terraform save the state of the infrastructure in a storage, these files have the extension **.tfstate**. In MetTel Automation we
saves these files in a protected Cloud storage to centralize the states and be accessible each time the pipeline needs to deploy/update
the infrastructure.

## Folder structure

````bash
infra-as-code/
├── basic-infra             # basic infrastructure in AWS
└── data-collector          # data-collector infrastructre in AWS
└── dev                     # AWS resources for each environment (ECS Cluster, ElastiCache Cluster, etc.)
└── kre                     # kre infrastructure
  └── 0-create-bucket       # bucket to store EKS information
  └── 1-eks-roles           # IAM roles infrastructure for EKS cluster
  └── 2-smtp                # SES infrastructure folder
└── kre-runtimes            # kre runtimes infrastructure
  └── modules               # custom terraform modules folders used for create KRE infrastructure
  └── runtimes              # KRE runtimes folders
└── network-resources       # network resources infrastructure in AWS
````

Al terraform files are located inside `./infra-as-code`, in this folder there are four additional folders, `basic-infra`, `dev`, `ecs-services` and `network-resources`.

1. `basic-infra`: there are the necessary terraform files to create the Docker images repositories in ECS, and the roles and policies necessary for use these.

2. `data-collector`: there are the necessary terraform files to create a Lambda, a DocumentDB Cluster, as well as an API Gateway to call the necessary and all the necessary resources to perform the conexion between these elements.

    > These resources will only be created for production environment

3. `dev`: there are the necessary terraform files for create the resources used for each environment in AWS, these are as follows

    * An [ECS Cluster](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ECS_clusters.html), the [ECS Services](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs_services.html) and its [Task Definition](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/example_task_definitions.html) for all the microservices present in the project

    * Three [ElastiCache Redis Clusters](https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/WhatIs.html)

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

    * A set of [null_resource](https://www.terraform.io/docs/providers/null/resource.html) *Terraform* type resources to execute the [python script in charge of health checking the task instances](../ci-utils/ecs/task_healthcheck.py) created in the deployment of capabilities microservices.

4. `kre`: there are the necessary terraform files for create the infrastructure for the [kre](https://github.com/konstellation-io/kre) component of [konstellation](https://konstellation-io.github.io/website/), as well as all the components it needs at AWS.

    There is a series of folders with terraform code that have a number in their names, these will be used to deploy the components in a certain order and are detailed below:

    - `0-create-bucket`: In this folder the terraform code is available to create a bucket for each environment and save information about the cluster, such as the SSH key to connect to the worker nodes of the EKS cluster that is going to be created.

    - `1-eks-roles`: In this folder the terraform code is available to create different IAM roles to map with EKS users and assign specific permissions for each one, for this purpose, a [cli](../ci-utils/eks/iam-to-eks-roles/README.md) will be used later.

    - `2-create-eks-cluster`: In this folder the terraform code is available to create the following resources
    
        - An [EKS cluster](https://docs.aws.amazon.com/eks/latest/userguide/clusters.html) to be able to deploy the different kre components designed for Kubernetes

        - An [AutoScaling Group](https://docs.aws.amazon.com/autoscaling/ec2/userguide/AutoScalingGroup.html) to have the desired number of Kubernetes worker nodes

        - A hosted zone on [Route53](https://aws.amazon.com/route53/faqs/?nc1=h_ls) for the corresponding kre environment

        - A SSH key to connect to any worker node of EKS

    - `3-smtp`: In this folder the terraform code to create a SMTP service through [Amazon SES](https://aws.amazon.com/ses/) and all the necessary components of it.

5. `kre-runtimes`: there are the necessary terraform files for create the infrastructure needed by a KRE runtime:
    - `modules`: Contains the terraform code for custom modules created for provision a KRE runtimes. It will create the following for each KRE runtime:
        - A Route53 Hosted Zone in `mettel-automation.net` domain.

    - `runtimes`: Contains the terraform code files for deploy KRE runtimes used the custom module located in `modules` folder.

6. `network-resources`: there are the necessary terraform files for create the [VPC](https://aws.amazon.com/vpc/) and all related resources in the environment used for deployment, these being the following:

    * [Internet Gateway](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Internet_Gateway.html)

    * [Elastic IP Addresses](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/elastic-ip-addresses-eip.html)

    * [NAT Gateways](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-nat-gateway.html)

    * [Subnets](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Subnets.html)

    * [Route tables](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Route_Tables.html) for the created subnets

    * A set of [Security Groups](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-security-groups.html) for all the resources created by the terraform files present in this folder
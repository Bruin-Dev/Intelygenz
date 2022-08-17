## Pre requisites
- [AWS user credentials](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html)
- [AWS SSH keys credentials](https://docs.aws.amazon.com/codecommit/latest/userguide/setting-up-ssh-unixes.html)
- Verify [AWS Personal Health Dashboard](https://phd.aws.amazon.com/)
- Verify [AWS Services Health Dashboard](https://health.aws.amazon.com/health/status)


## Description
The Automation Engine application is prepared to be deployed in different AWS regions, each region is associated with an `environment`.
At this moment we have two environments: `pro` and `mirror` in `us-east-1` and `us-west-1` respectively; but we can have more in the future.
By default the application is deployed in `pro` environment but can change by updating a variable in the repository.
This way if we suffer a disaster and lose the main region we can easily deploy the application in the mirror region,
this is the goal of this procedure.


## Considerations
- Ensure that your AWS credentials have Codecommit permission to interact with Automation Engine repository in all available regions.
- We have configured a git mirroring from `pro` to `mirror` environment, by that way we always have updated the repo in the mirror region.
- The actual environments are: `pro` and `mirror`, but could be more in the future.
- Master branch is protected, you can't commit directly to it, you must create a new branch and do a pull request.
- An authorized team member must accept your PR once the changes was verified.
- Once the pipeline run, if we check logs, we can verify that is possible that terraform failed the execution of `union` resources(AWS resources
that create links between regions), this is originated by AWS unavailability in one region. This behavior is expected since we assume
that an AWS Region is not working properly; this job is allowed to fail for this reason, if any other task fails the pipeline will end with an error.

## Posible situation
We have all active infrastructure and application in `pro` (`us-east-1`), then AWS suffer a disaster in Nort Virginia region(`us-east-1`) and
we lost the activity and respondes from AWS resources; we must assume that all resources are unavailable.
It's time to star using the resources in the mirror region(`us-west-1`) by following the next steps:

## Steps
- Verify AWS Health Dashboards to confirm AWS services availabily per region. Confirm that our services in the main region(`us-east-1`) are unavailable.
- Clone the repository from the mirror region(`us-west-1`): 
  ```
  git clone ssh://git-codecommit.us-west-1.amazonaws.com/v1/repos/fedramp-automation-engine
  ```
- Create a new branch with the name `switch-automation-engine-region`.
  ```
  cd fedramp-automation-engine
  git branch -b switch-automation-engine-region
  ```
- Edit `ACTIVE_ENVIRONMENT` default value in `infra-as-code/basic-infra/common_info.tf` file 
  ```
  variable "ACTIVE_ENVIRONMENT" {
    default     = "pro"                               <---- put the desired environment here, example: "mirror"
    description = "Active environment in aws"
  }
  ```
- Push the changes to the repository:
  ```
  git commit
  git push
  ```
- Go to AWS Codecommit console in mirror region(`us-west-1`), in [pull request section of the automation repo](https://us-west-1.console.aws.amazon.com/codesuite/codecommit/repositories/fedramp-automation-engine/pull-requests?region=us-west-1&status=OPEN&) and create a new PR
- After the approve from the authorized team member, merge to master in the same AWS codecommit console.

## Git merge results
Once the merge is complete, this will trigger a pipeline in the mirror region(`us-west-1`) that will create the infrastructure based in the variable `ACTIVE_ENVIRONMENT`, 
this means that the application will be deployed in the region where we previously confirm that AWS has no issues.
## Pre requisites
- [AWS user credentials](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html)
- [AWS SSH keys credentials](https://docs.aws.amazon.com/codecommit/latest/userguide/setting-up-ssh-unixes.html)
- [Terraform](https://www.terraform.io/)

## Description
The Automation Engine project at this moment is deployed in AWS infrastructure with all [FEDRAMP](https://www.fedramp.gov/)
requirements meet, this is the reason why we select the CI/CD tool of AWS to manage the application life cycle; to take advantage of the
OKTA and AWS SSO access, permission and logs of every action in the Automation APP.
To init the project and be able to start using these CI/CD tool we need to follow a manual steps. 


## Considerations
- Ensure that your AWS credentials have the required permissions to create the [listed resources](#application-results), if not terraform will fail.
- In terraform we use a feature called `workspace` as a representation of the `environment`.
- The actual environments are: `pro` and `mirror`, but could be more in the future.
- Any change must be applied manually in all regions and pushed to the repository by the authorized operator.
- The definition of this resources are located in a separated repository of Automation Engine one.
- A manual git repository was already created that contain the terraform definition of the CI/CD tool in the master branch.
- This manual repository has subsequently created a job in the pipelines (automated) that performs backups together with the rest of the infrastructure.


## Steps
- Configure AWS credentials by follow [the official docs](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html).
- Configure AWS SSH keys credentials by follow [the official docs](https://docs.aws.amazon.com/codecommit/latest/userguide/setting-up-ssh-unixes.html).
- Clone the repository: 
  ```
  git clone ssh://git-codecommit.us-east-1.amazonaws.com/v1/repos/fedramp-pipelines
  ```
- CD to the repo folder
  ```
  cd fedramp-pipelines/
  ```
- Initializate terraformn:
  ```
  terraform init
  ```
- Select workspace/environment:
  ```
  terraform workspace select <environemt>
  ```
- Verify changes and apply (if theres a problem in the plan step, just fix an try again):
  ```
  terraform plan
  terraform apply
  ```
- Do the last two steps for the other environments
- Push the changes to the repository:
  ```
  git commit
  git push
  ```

## Application results
Afther terraform apply of all environments, the pipelines will be configured in each separated region and will be prepared to mange
Automation Engine application life cycle.
This terraform project will create the follow resources in each environment:

- aws_codebuild_project.stages["deploy"]
- aws_codebuild_project.stages["integrity"]
- aws_codebuild_project.stages["observability"]
- aws_codebuild_project.stages["terraform"]
- aws_codebuild_project.stages["validate"]
- aws_codecommit_approval_rule_template.approval
- aws_codecommit_approval_rule_template_association.approval_association
- aws_codecommit_repository.git
- aws_codepipeline.pipeline_master
- aws_iam_policy.pipelines
- aws_iam_role.pipelines
- aws_iam_role_policy_attachment.pipelines
- aws_s3_bucket.pipelines
- aws_s3_bucket_acl.pipelines
- aws_security_group.codebuild

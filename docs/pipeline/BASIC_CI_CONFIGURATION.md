<div align="center">
<img src="http://photos.prnewswire.com/prnfull/20141022/153661LOGO?p=publish"  width="300" height="120">
</div>

# Setting up the CI/CD from scratch
To release this project and make it work, we first need to set up the following items:

- [Semantic Release](#semantic-release)
- [AWS](#aws)
- [AIVEN](#aiven)
- [Snowflake](#snowflake)

## Semantic Release
Semantic release depends on a base image stored on the GitLab repository that makes pipelines able to finish in a reasonable amount
of time.

The only two configurations we need to make it work are:

- Make sure that the base image repository is ready to be used, and point to that image in the project's root `.gitlab-ci.yml`
  through the variable `SEMANTIC_RELEASE_IMAGE`.

- Get an access token on the project (`Settings > Access tokens`), and get all permissions required to interact with the API.

    After getting the access token, make sure to create a variable called `GITLAB_TOKEN` and set its value with it.

## AWS
It is recommended to create an account for Terraform and a group of permissions with admin access. It is also necessary to create
an AWS S3 bucket that the user can access to.

To connect to AWS from some steps of the CI/CD, we need to add the following variables to `Settings > CI/CD`:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

> Make sure NOT to add these configurations to the project's root `.gitlab-ci.yml` to avoid potential security risks.

These two variables are mandatory for the CI/CD to be able to connect to the AWS S3 bucket, as we store Terraform's `tfstate` files to
_remember_ the state of our infrastructure deployments.

## AIVEN

_TODO_

## Snowflake

_TODO_
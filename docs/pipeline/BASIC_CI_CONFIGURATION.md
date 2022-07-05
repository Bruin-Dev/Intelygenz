<div align="center">
<img src="http://photos.prnewswire.com/prnfull/20141022/153661LOGO?p=publish"  width="300" height="120">
</div>

# 1. CI/CD PROJECT CONFIGURATION FROM 0
To release this project an make it work we need to configure next stuff:
- semantic release
- AIVEN
- AWS

# 1.1 Semantic Release
Semantic release is depending of a base image in this repository to be faster on this project CI/CD. The only two configurations
we need to make it work here is:
- Have prepared the base image repository and point to that image in the .gitlab-ci.yml(variable SEMANTIC_RELEASE_IMAGE)
- Get an access token on the project (Settings/Access tokens) and get all permissions to interacts with the API. Create a variable called GITLAB_TOKEN and put the token you crete there.

# 1.2 AIVEN
_TODO_

# 1.3 AWS
It's recommended to create an account for terraform and a group of permissions with admin access, also it's necessary to create
an S3 bucket that the user can access to. To accomplish aws connection in some steps of the CI/CD we need to add next 
variables (on the settings section, not in the YAML) in the CI:
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY

It's necessary to connect to the S3 from amazon, where we store the tfstate files to maintain the state of 
our infrastructure deployments.

# 1.4 Snowflake

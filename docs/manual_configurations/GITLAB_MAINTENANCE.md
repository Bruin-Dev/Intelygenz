<div align="center">
<img src="http://photos.prnewswire.com/prnfull/20141022/153661LOGO?p=publish"  width="300" height="120">
</div>

# 1. Summary

Gitlab is the tool selected to manage CI-CD process of Automation-Engine APP. The source code is in the [project repository](https://gitlab.fedramp.mettel-automation.net/mettel/fedramp-automation-engine), under "builder" workspace of Terraform definition located in `infra-as-code/basic-infra`. This nevironment only require the modules `1-parameters`, `2-network` and `4-services`.

Gitlab is deployed in a separated environemt (workspace) of automation-engine application, so the changes applied in this workspace not afect the main app.

Gitlab is the basis for CI-CD, so it cannot manage its own lifecycle (it could be the snake biting its own tail). So the integration and maintenance of this environment is managed locally with Terraform by the infrastructure administrators, keeping the code versions in the repository of the project itself.

# 2. Modules

`1-parameters`, define the parameter required by the workspace "builder", like password of the database or gitlab root account. The parameter creation are managed by terraform, but the value is updated by operators in AWS parameter store.

`2-network`, manage the networking of the environemt, this terraform configuration have all the VPC configuration required to deploy gitlab.

`4-services`, deploy AWS services required like RDS, EKS, or S3 among others. Also deploy the Chart of the gitlab application.

# 3. Deploy

All terraform modules have a common `Makefile` that contain the required configuratión to apply terraform in a specifig workspace. For example, to deploy the complete gitlab environment you need to:
```
cd infra-as-code/basic-infra/1-parameters
make terraform_apply env=builder
  // note: after parameter creation, you need to update the value of that paramters in AWS web console.
cd ../2-network
make terraform_apply env=builder
cd ../4-services
make terraform_apply env=builder
```

# 4. Updates

Gitlab receives constant security patches and updates, it is recommended to keep gitlab up to date. To do this, we go to the `gitlab-ci.yml` root file of the repo and update the version, for example:
```
  ...
  TF_VAR_GITLAB_CHART_VERSION: "6.0.3"
  ...
```
Then just execute in `4-services` folder the command: `make terraform apply env=builder` verify the changes, and accepting them by write "yes" to applied it.

# 5. References

* https://docs.gitlab.com/ee/raketasks/backup_restore.html
* https://gitlab.com/gitlab-org/charts/gitlab/-/blob/master/doc/backup-restore/index.md
* https://gitlab.com/gitlab-org/charts/gitlab/blob/master/doc/backup-restore/restore.md
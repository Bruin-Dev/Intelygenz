<div align="center">
<img src="http://photos.prnewswire.com/prnfull/20141022/153661LOGO?p=publish"  width="300" height="120">
</div>

# 1. Summary

Thes process requires one workday and doesn't affect the functionality of the Automation-Engine production environment.

Gitlab is deployed with the [Automation-Engine fedramp repository](https://gitlab.fedramp.mettel-automation.net/mettel/fedramp-automation-engine), is under "builder" workspace of Terraform definition located in `infra-as-code/basic-infra`. The deployment, maintenance, and updates are managed locally by the infrastructure team as explained [here](../manual_configurations/GITLAB_MAINTENANCE.md).

Gitlab has most of its configuration files saved in external storage, we use AWS S3 for all objects and AWS RDS (PostgreSQL) for the database; all of this is in `US-EAST-1` region. Gitlab has its own process to make backups every day at 06:00 (UTC+02:00) which also includes a Postgres backup and is also saved in S3. All S3 buckets are replicated in `US-WEST-1` region so we have backups of GitLab backups on the opposite coast of the united states in case of disaster failure in the main region.

Aditionally to this, we require the `secrets.yml` config file that have the certificates that gitlab creates on his first deploy to use internally. This file is exported and saved in `1password`, with the name “GITLAB FedRAMP rails secret backup” and the file name is `gitlab-secrets.yaml`. This file is required if we want to redeploy gitlab and restore the backup.

The backups contain:
* db (database)
* uploads (attachments)
* builds (CI job output logs)
* artifacts (CI job artifacts)
* lfs (LFS objects)
* terraform_state (Terraform states)
* registry (Container Registry images)
* pages (Pages content)
* repositories (Git repositories data)
* packages (Packages)

# 2. Recovery

* Deploy required infrastructure. 

1. Use the `infra-as-code/basic-infra` folder, only need: `1-parameters`, `2-network` and `4-services`. The terraform workspace is `builder`.
2. Set the required parameters, check de `data.tf` file in parameters section.
3. Change the name of the buckets to avoid conflicts. (files `4-services/s3.tf` and `4-services/s3-cross-replica`)
4. For deploying the required infra in a new region only need to change Terraform Local variable called `region` (file `locals.tf`) with the new region in the 3 folders.
5. Define a secundary region (file `4-services/terraform_config.tf`) to set the new S3 bucket replicas in another region if main is not available to be the replica. Or if dont want to create the replicas only change the name of the terrafform file (example `s3-cross-replica.back`)

* Install a clean gitlab helm chart with the same version of the backup.

* Restore the `gitlab-rails-secret.yaml` as a secret in the cluster:

1. Find the object name for the rails secrets:
````
kubectl -n gitlab get secrets | grep rails-secret
````

2. Delete the existing secret:

```    
kubectl delete secret <rails-secret-name> (gitlab-rails-secret)
```

3. Create the new secret using the same name as the old, and passing in your local YAML file:
```
 kubectl create secret generic <rails-secret-name> --from-file=secrets.yml=gitlab-secrets.yaml
```

4. In order to use the new secrets, the Webservice, Sidekiq and Toolbox pods need to be restarted. The safest way to restart those pods is to run:
```
kubectl delete -n gitlab pods -lapp=sidekiq,release=<helm release name>
kubectl delete -n gitlab pods -lapp=webservice,release=<helm release name>
kubectl delete -n gitlab pods -lapp=toolbox,release=<helm release name>
```

* Restore the backup file:

1. Ensure the Toolbox pod is enabled and running by executing the following command
```
kubectl get pods -lrelease=RELEASE_NAME,app=toolbox
```

2. Get the tarball ready in S3 bucket. Make sure it is named in the [timestamp]_[version]_gitlab_backup.tar format.

3. Run the backup utility to restore the tarball
```
kubectl exec <Toolbox pod name> -it -- backup-utility --restore -t <timestamp>_<version>
```
4. Here, <timestamp>_<version> is from the name of the tarball stored in gitlab-backups bucket. In case you want to provide a public URL, use the following command
```
kubectl exec <Toolbox pod name> -it -- backup-utility --restore -f <URL>
```
***NOTE***: *You can provide a local path as a URL as long as it's in the format: file://<path>*
*This process will take time depending on the size of the tarball.*
*The restoration process will erase the existing contents of database, move existing repositories to temporary locations and extract the contents of the tarball. Repositories will be moved to their corresponding locations on the disk and other data, like artifacts, uploads, LFS etc. will be uploaded to corresponding buckets in Object Storage.*
*During restoration, the backup tarball needs to be extracted to disk. This means the Toolbox pod should have disk of necessary size available. For more details and configuration please see the Toolbox documentation.*

* Restore the runner registration token:
    after restoring, the included runner will not be able to register to the instance because it no longer has the correct registration token (token has been changed with the new GitLab chart installation). 

1. Find the new shared runner token located on the admin/runners webpage of your GitLab installation.
```
kubectl get secrets | grep gitlab-runner-secret
```

2. Find the name of existing runner token Secret stored in Kubernetes
```
kubectl delete secret <runner-secret-name>
```

3. Delete the existing secret
```
kubectl delete secret <runner-secret-name>
```

4. Create the new secret with two keys, (runner-registration-token with your shared token, and an empty runner-token)
```
 kubectl create secret generic <runner-secret-name> (gitlab-gitlab-runner-secret) --from-literal=runner-registration-token=<new-shared-runner-token> (gitlab-gitlab-runner-token-xxxxx) --from-literal=runner-token=""
```

* (optional) Reset the root user’s password:
    The restoration process does not update the `gitlab-initial-root-password` secret with the value from backup. For logging in as root, use the original password included in the backup. In the case that the password is no longer accessible, follow the steps below to reset it.
    
1. Attach to the Webservice pod by executing the command
```
kubectl exec <Webservice pod name> (gitlab-webservice-default-xxxxx-xxxxx) -it -- bash
```

2. Run the following command to reset the password of root user. Replace #{password} with a password of your choice
```
/srv/gitlab/bin/rails runner "user = User.first; user.password='#{password}'; user.password_confirmation='#{password}'; user.save!"
```

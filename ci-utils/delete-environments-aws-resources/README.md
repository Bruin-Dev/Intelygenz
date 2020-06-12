# Delete environments aws resources

In the folder a series of *Python* files are stored, these allow the deletion of the resources created in AWS associated to an environment.

>It is important to remember that the names for environments are `automation-master` for production, as well as `automation-<branch_identifier>` for ephemeral environments, being `branch_identifier` the result of applying `echo -n "<branch_name>" | sha256sum | cut -c1-8` on the branch name related to the ephemeral environment.

## Usage <a name="delete-environments-aws-resources_usage"></a>

In order to be able to use the CLI mentioned previously it is necessary to previously define the AWS credentials, for this it is necessary to define the environment variables `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in the following way:

```sh
$ export AWS_ACCESS_KEY_ID=<access_key>
$ export AWS_SECRET_ACCESS_KEY=<secret_key>
```

Once the AWS credentials have been configured, it is possible to use the script in the following way:

```bash
python main.py -e <environment_name> [commands]
```
>To use any command it's necessary to specify the environment name as the first argument of the `main.py` script through the -e parameter.

## Commands <a name="delete-environments-aws-resources_commands"></a>

CLI supports a number of commands. These are explained below:

- `-a`, `--all`: All the resources in AWS associated to the specified environment will be deleted, carrying out the corresponding orderly deletion of them so as not to produce dependency errors during the process.

    >**If this option is specified, any other option will be ignored.**
- `-c`, `--ecs-cluster`: The ECS cluster associated to the environment provided will be removed, as well as all the resources related to it:
  
  - *ECS Services* defined in the ECS cluster and *Tasks* of each one of them.
  
  - *Namespaces* and *Services* associated with the same to perform [*Services Discovery*](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-discovery.html) in the cluster

- `-d`, `--service-discovery`: The *namespace* created for the *Service Discovery* of the environment provided will be deleted, previously all the services associated to that namespace will be deleted.

- `-r`, `--redis-cluster`: The *ElastiCache Redis Cluster* associated to the specified environment will be removed.

- `-l`, `--load-balancer`: The *Application Load Balancer (ALB)* associated to the specified environment will be removed, as well as all the resources related to it (*Target Groups*).

- `-s`, `--security-groups`: All the *Security Groups* associated to the different resources created in *AWS* for the specified environment will be removed.

- `-m`, `--metrics`: All the resources related to metrics created for the specified will be removed, being these the ones specified below:

  - *CloudWatch Alarms*
  
  - *CloudWatch Dashboard*

  - *CloudWatch Log Filters*

- `-z`, `--hosted-zones`: All the record set created for specified environment in hosted zone with name `mettel-automation.net` in *AWS Route53 Service* will be deleted.

- `-f`, `--cloud-formation`: The *Cloud Formation Stack* resources created for the specified environment will be removed

- `-b`, `--buckets`: All *Terraform* files with `tfstate` extension related to the specified environment will be deleted, these are used to know the state of the resources created by it and are stored in an  *S3 Bucket* that is specified in the creation of its with *Terraform*.
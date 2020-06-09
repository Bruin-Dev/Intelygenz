# AWS nuke conf generator
This [script](./aws_nuke_conf_generator.py) has been implemented to generate the configuration file used by [`aws-nuke`](https://github.com/rebuy-de/aws-nuke) to delete resources in AWS.

The generated configuration file will allow filtering on the resources to be deleted specified in it, so that `aws-nuke` will only delete those associated with the environment specified in that file. The resources to be deleted specified in this file are the following:

- *ElasticacheCacheCluster*
- *ElasticacheSubnetGroup*
- *ELBv2*
- *ELBv2TargetGroup*
- *CloudFormationStack*
- *CloudWatchAlarm*
- *CloudWatchLogsLogGroup*
- *ServiceDiscoveryNamespace*
- *ServiceDiscoveryService*
- *ECSCluster*
- *ECSService*
- *ECSTaskDefinition*
- *EC2SecurityGroup*

In order to carry out this process of generating a configuration file, a [template file](./config_template.yml) is used on which the script applies the relevant changes to the resources to be filtered.

### Usage <a name="aws_nuke_conf_generator_usage"></a>

In order to be able to use the [script](./aws_nuke_conf_generator.py) mentioned previously it is necessary to previously define the AWS credentials, for this it is necessary to define the environment variables `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in the following way:

```sh
$ export AWS_ACCESS_KEY_ID=<access_key>
$ export AWS_SECRET_ACCESS_KEY=<secret_key>
```

Once configured the AWS credentials, it is possible to use the [script](./aws_nuke_conf_generator.py) to create the configuration file that will be used by `aws-nuke` to delete the AWS resources associated to the specified environment, it is necessary to specify this one, using the `-e` option, as shown below:

```sh
$ python ci-utils/aws-nuke/aws_nuke_conf_generator.py -e <environment_name>
```

>It is important to remember that the names for environments are `automation-master` for production, as well as `automation-<branch_identifier>` for ephemeral environments, being `branch_identifier` the result of applying `echo -n "<branch_name>" | sha256sum | cut -c1-8` on the branch name related to the ephemeral environment.

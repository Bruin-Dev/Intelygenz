# IAM to EKS Roles

**Table of contents**:
- [Description](#description)
- [Configuration](#configuration)
  - [Roles Permissions Configuration](#roles-permissions-configuration)
- [Usage](#usage)

## Description

This [cli](./app.py) has been developed in *Python* for working with IAM Roles and RBAC of an [EKS](https://docs.aws.amazon.com/eks/latest/userguide/getting-started.html) Cluster.

The objective of this [cli](./app.py) is to obtain certain [IAM roles](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html), filtering by their tags to create users in the EKS cluster with certain `ClusterRoles` and each `ClusterRoleBinding` for the users associated with each `ClusterRole`. 

The `ClusterRole` created in the EKS cluster will be associated with a series of permissions on the cluster's resources.

## Configuration

This cli uses a [configuration file](./config.py) to establish the relationship between the roles to be created and the permissions on the Kubernetes API using the Kubernetes [RBAC authorization](https://kubernetes.io/docs/reference/access-authn-authz/rbac/).

### Roles Permissions Configuration

The following is an example configuration file where the different roles are configured through the `CLUSTER_ROLES_PERMISSIONS` element, where each of the elements is a role to be created. In each one of the roles, a list of dictionaries is defined with the permissions that they will have on Kubernetes.

```sh
CLUSTER_ROLES_PERMISSIONS = {
    "developer": {
        "rules": [
            {
                "apiGroups": [""],
                "resources": ["pods"],
                "verbs": ["get", "list", "watch"]
            },
        ],
        "apiVersion": "rbac.authorization.k8s.io/v1"
    },
    "developer-ops-privileged": {
        "rules": [
            {
                "apiGroups": ["", "apps"],
                "resources": ["*"],
                "verbs": ["*"]
            },
        ],
        "apiVersion": "rbac.authorization.k8s.io/v1"
    },
    "devops": {
        "rules": [
            {
                "apiGroups": ["*"],
                "resources": ["*"],
                "verbs": ["*"]
            },
        ],
        "apiVersion": "rbac.authorization.k8s.io/v1"
    }
}
```

### Cluster Roles Binding Configuration

In the mentioned configuration file the API endpoint of Kubernetes to be used for the assignment between the ClusterRole and the users assigned to it is also set, for this purpose a ClusterRoleBinding will be created for each of them.

The following is an example configuration file where the configuration mentioned previously related with the API endpoint of `ClusterRoleBinding`. This configuration is done through the `CLUSTER_ROLE_BINDING_CONFIG` element in the configuration file.

```sh
CLUSTER_ROLE_BINDING_CONFIG = {
    "apiVersion": "rbac.authorization.k8s.io/v1",
    "roleRef": {
        "apiGroup": "rbac.authorization.k8s.io",
        "kind": "ClusterRole"
    }
}
```

## Usage

In order to use this [script](./app.py) it is necessary to perform the following steps previously:

- Define the AWS credentials, this can be down in two ways:

  - Defining the environment variables `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in the following way:

      ```sh
      $ export AWS_ACCESS_KEY_ID=<access_key>
      $ export AWS_SECRET_ACCESS_KEY=<secret_key>
      ```

  - Use an aws profile, in case of not wanting to use the one defined by default you can configure which one you want to use through the variable `AWS_PROFILE` as explained below:
    ```bash
    $ export AWS_PROFILE=<aws_profile_name>
    ```

- Install the python packages required by the cli, these are specified in the [`requirements.txt`](./requirements.txt) file and are installed through the following command:

  ```bash
  $ pip3 install -r requirements.txt
  ```

To use this script it is necessary to invoke it providing value for a number of parameters:

- `-a/--aws_profile`: Optional flag to indicate the aws profile to be used. If none is indicated, the client will try to use the profile present in the 'AWS_PROFILE' variable or the credentials loaded through the corresponding environment variables.

- `-r/--aws_region`: Optional flag to indicate the region of aws to be used by the client. In case of not indicating a value for this flag it will use the value `us-east-1`.

- `-p/--project-tag`: Flag used to indicate the project name tag, this will be used to locate the IAM roles used in AWS that will be linked to the corresponding ClusterRole and its permissions.

- `--project-role`: Flag to indicate the role of the IAM users in the project, this will also be the role to search in the [configuration file](./config.py) to assign the corresponding permissions in the `ClusterRole` to be created in Kubernetes.

Once the previous step have been carried out, it is possible to use this [cli](./app.py) in the following way: 

```bash
$ python3 app.py -p mettel-automation-kre --project-role-tag developer
```
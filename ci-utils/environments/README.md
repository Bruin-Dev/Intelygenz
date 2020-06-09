# Environments utils

A number of scripts developed in bash for naming environments are stored in this folder.

**Table of contents**:
- [environment_assign](#environment_assign)
  - [Description](#environment_assign_description)
  - [Usage](#environment_assign_usage)

## Script environment_assign<a name="environment_assign"></a>

### Description <a name="environment_assign_description"></a>

This [script](./environment_assign.sh) has been developed in bash for naming environments.

### Usage <a name="environment_assign_usage"></a>

In order to use this [script](./environment_assign.sh) it is necessary to perform the following steps previously:

- Define the name of the branch

    ```sh
    $ export CI_COMMIT_REF_SLUG=<branch_name>
    ```
    >It is important to remember that the names for environments are `automation-master` for production (`master` branch), as well as `automation-<branch_identifier>` for ephemeral environments, being `branch_identifier` the result of applying `echo -n "<branch_name>" | sha256sum | cut -c1-8` on the branch name related to the ephemeral environment.

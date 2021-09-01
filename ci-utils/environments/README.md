# Environments utils

A number of scripts developed in bash for naming environments are stored in this folder.

**Table of contents**:
- [environment_assign](#script-environment_assign)
  - [Description](#description)
  - [Usage](#usage)

## Script environment_assign

### Description

This [script](./environment_assign.sh) has been developed in bash for naming environments.

### Usage

In order to use this [script](./environment_assign.sh) it is necessary to perform the following steps previously:

- Define the name of the branch

    ```sh
    $ export CI_COMMIT_REF_SLUG=<branch_name>
    ```
    >It is important to remember that the names for environments are `automation-master` for production (`master` branch), as well as `automation-<branch_identifier>` for ephemeral environments, being `branch_identifier` the result of applying `echo -n "<branch_name>" | sha256sum | cut -c1-8` on the branch name related to the ephemeral environment.

# ECR utils

In this folder are stored a series of scripts implemented in python used to manage the docker images stored in ECR.

**Table of content:**

- [CLI manage_ecr_docker_images](#CLI-manage_ecr_docker_images)
  - [Description](#description)
  - [Usage](#usage)

## CLI manage_ecr_docker_images

### Description

This [command line tool](./manage_ecr_docker_images.py) has been implemented in *Python*, it can be used for any of the following functions:

- Get the most recent image from a repository or all repositories of the images used in the project for an environment

- Delete all images in a repository or from all repositories in an environment. It is possible to delete only the oldest images, always leaving two images per repository in the environment.

## Commands

CLI supports a number of commands. These are explained below:

- `-e`, `--environment`: String flag to indicate the name of the environment with which actions will be performed.
  >It is necessary to provide a value for this flag.

- `-g`, `--get`: Boolean flag to indicate that retrieval actions will be performed on the docker images from one or more repositories (Default value: *False*).

- `-d`, `--delete`: Boolean flag to indicate that deletion actions will be performed on the docker images from one or more repositories (Default value: *False*).

  > It is necessary to indicate the value *True* for one of the flags `-g/--get` or `-d/--delete`, otherwise the CLI will launch an execution error.

- `-r`, `--repository`: String flag to indicate the name of the repository on which actions will be performed.

- `a`, `--all_repositories`: Boolean flag to indicate whether actions will be taken on all docker image repositories or not (Default value: *False*).

- `o`, `--oldest_images`: Boolean flag to indicate whether only the oldest images will be removed from the provided repositories. **Actions will only be deleted when there are more than two images for the repository, always leaving the two most recent images for each repository.** 

### Usage

In order to use this [CLI](./manage_ecr_docker_images.py) it is necessary to perform the following steps previously:

- Define the AWS credentials, for this it is necessary to define the environment variables `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_DEFAULT_REGION` in the following way:

    ```sh
    $ export AWS_ACCESS_KEY_ID=<access_key>
    $ export AWS_SECRET_ACCESS_KEY=<secret_key>
    $ export AWS_DEFAULT_REGION=<aws_region>
    ```

    > The default AWS region used in the project is us-east-1

Once the AWS credentials have been configured, it is possible to use the script for the different actions:

- Obtain the most recent Docker images of an environment, there are two possibilities:
   - Get the latest images from a repository for an environment
     ```sh
     $ python3 manage_ecr_docker_images.py -e <environment_name> -g True -r <docker_repository_name>
     ```

   - Get the latest images from all repositories from an environment:
     ```sh
     $ python3 manage_ecr_docker_images.py -e <environment_name> -g True -a True
     ```

- Delete Docker images of an environment, there are four possibilities:

  - Delete the oldest images from a repository for an environment In this case, images will always be deleted, keeping the two most recent ones.
    ```sh
    $ python3 manage_ecr_docker_images.py -e <environment_name> -d True -o True -r <docker_repository_name>
    ```

  - Delete the oldest images from all repositories for an environment In this case, images will always be deleted, keeping the two most recent ones.
    ```sh
    $ python3 manage_ecr_docker_images.py -e <environment_name> -d True -o True -a True
    ```

  - Delete all the images from a repository for an environment:
    ```sh
    $ python3 manage_ecr_docker_images.py -e <environment_name> -d True -r <docker_repository_name>
    ```

  - Delete all the images from all repositories from an environment:
    ```sh
    $ python3 manage_ecr_docker_images.py -e <environment_name> -d True -a True
    ```
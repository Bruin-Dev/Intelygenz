# ECR utils

In this folder are stored a series of scripts implemented in bash and python used to manage the docker images stored in ECR.

**Table of content:**

- [Script manage_ecr_docker_images](#manage_ecr_docker_images)
  - [Description](#manage_ecr_docker_images_description)
  - [Usage](#manage_ecr_docker_images_usage)
- [Script assign_docker_images_build_numbers](#assign_docker_images_build_numbers)
  - [Description](#assign_docker_images_build_numbers_description)
  - [Usage](#assign_docker_images_build_numbers_usage)

## Script manage_ecr_docker_images <a name="manage_ecr_docker_images"></a>

### Description <a name="manage_ecr_docker_images_description"></a>

This [script](./manage_ecr_docker_images_description.py) has been implemented in *Python*, it can be used for any of the following functions:

- Get the oldest image from an ECR repository provided as a parameter in a given environment. In case that repository has more than two images in the provided environment, it will perform the deletion of the oldest image according to the ECR upload date.

- Obtain the most up-to-date image of all the ECR repositories used in the project by saving each one of them in a JSON file for each of the repositories with the following format

   ```bash
   {
       "tag": <ecr_repository_tag>
   }
   ```

### Usage <a name="manage_ecr_docker_images_usage"></a>

In order to use this [script](./manage_ecr_docker_images_description.py) it is necessary to perform the following steps previously:

- Define the AWS credentials, for this it is necessary to define the environment variables `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_DEFAULT_REGION` in the following way:

    ```sh
    $ export AWS_ACCESS_KEY_ID=<access_key>
    $ export AWS_SECRET_ACCESS_KEY=<secret_key>
    $ export AWS_DEFAULT_REGION=<aws_region>
    ```

    > The default AWS region used in the project is us-east-1

- Declare the variable `ENVIRONMENT_VAR` with the value of the environment on which you it is going to to used in the following way:

    ```sh
    $ export ENVIRONMENT_VAR=<environment_name>
    ```

    >It is important to remember that the names for environments are `automation-master` for production, as well as `automation-<branch_identifier>` for ephemeral environments, being `branch_identifier` the result of applying `echo -n "<branch_name>" | sha256sum | cut -c1-8` on the branch name related to the ephemeral environment.

Once the previous steps have been carried out, it is possible to use this [script](./check_ecs_resources.py) as shown below:

- To get the oldest image from a particular repository, provide the name of the repository using the -t option, as follows:

    ```sh
    $ python3 ci-utils/ecr/manage_ecr_docker_images.py -r <ecr_repository_name>
    ```

    >The nomenclature of the images in the project is `automation-<microservice_name>`

- To obtain the most up-to-date image for the environment provided in each of the repositories, simply indicate the -g option, as shown below:

   ```sh
   $ python3 ci-utils/ecr/manage_ecr_docker_images.py -g
   ```
  
 ## Script manage_ecr_docker_images <a name="assign_docker_images_build_numbers"></a>
 
 
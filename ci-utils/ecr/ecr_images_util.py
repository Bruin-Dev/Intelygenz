#!/usr/bin/env python3

import argparse
import json
import logging
import os
from datetime import datetime, timedelta
from distutils.version import StrictVersion

import boto3
from botocore.exceptions import ClientError

# Email configuration
SENDER = "Mettel Production Pipeline <mettel@intelygenz.com>"
RECIPIENT = "mettel@intelygenz.com"
AWS_REGION = "us-east-1"
CHARSET = "UTF-8"
BODY_TEXT = (
    "WARNING:\r\n"
    "This microservice will not be deployed."
    "Review the HELM pipeline job to get more"
    "information.\n\n"
    "If you do not want to deploy this microservice,"
    "this warning may be a false positive because it is"
    "a new service that has no releases yet, to avoid"
    "this warning in future versions upload an image for"
    "the microservice with tag 1.0.0"
)
BODY_HTML = """<html>
<head></head>
<body>
  <h1>WARNING:</h1>
  <p>This microservice will not be deployed. Review the
    <a href='https://gitlab.intelygenz.com/mettel/automation-engine/-/pipelines'>
    HELM pipeline job</a> to get more information.<br><br>
    If you do not want to deploy this microservice,
    this warning may be a false positive because it is
    a new service that has no releases yet, to avoid
    this warning in future versions upload an image for
    the microservice with tag 1.0.0
    .</p>
</body>
</html>
            """
# END Email configuration

logging.basicConfig(level=logging.INFO)


class EcrUtil:
    _client = boto3.client("ecr", region_name="us-east-1")
    _repositories_to_avoid = ["automation-python-3.6", "automation-python-3.6-alpine"]
    _environment_id_production = "production"
    _project_name = "mettel-automation"

    @staticmethod
    def _write_to_json_file(filename, content):
        file_dir = parser.parse_args().file
        with open(file_dir, "w+") as f:
            f.write(json.dumps(content, indent=4, default=str))
        return file_dir

    @staticmethod
    def _calculate_number_of_images_to_delete(docker_images_to_delete_in_repositories):
        total_images_to_delete = 0
        for repository in docker_images_to_delete_in_repositories:
            total_images_to_delete += len(repository["images_to_delete"])
        return total_images_to_delete

    def _check_is_project_repository(self, repository_name, repository_arn):
        logging.info(f"Checking if repository {repository_name} is an {self._project_name} repository")
        repository_tags_resp = self._client.list_tags_for_resource(resourceArn=repository_arn)
        if repository_tags_resp:
            repository_tags = repository_tags_resp.get("tags")
            if repository_tags:
                for tag in repository_tags:
                    if tag.get("Key") == "Project" and tag.get("Value") == self._project_name:
                        logging.info(f"Repository with name {repository_name} is a {self._project_name} repository")
                        return True
        return False

    def _get_all_ecr_repositories_from_aws(self):
        repositories_in_ecr = []
        repositories = self._client.describe_repositories()
        logging.info(f"Obtaining all ECR repositories to filter by project {self._project_name}")
        for repository in repositories["repositories"]:
            repository_arn = repository.get("repositoryArn")
            repository_name = repository.get("repositoryName")
            if self._check_is_project_repository(repository_name, repository_arn):
                repositories_in_ecr.append(repository_name)
        if len(repositories_in_ecr) > 0:
            repositories_in_ecr.sort()
            repositories_to_avoid = self._repositories_to_avoid
            repositories_in_ecr = [elem for elem in repositories_in_ecr if elem not in repositories_to_avoid]
        return repositories_in_ecr

    def _obtain_image_pushed_time(self, repository_name, image_tag):
        image_pushed_time = None
        logging.debug(f"Obtaining push time of Docker image with tag {image_tag} in repository {repository_name}")
        response = self._client.describe_images(
            repositoryName=repository_name,
            imageIds=[
                {"imageTag": image_tag},
            ],
        )
        if response["imageDetails"]:
            image_pushed_time = response["imageDetails"][0]["imagePushedAt"]
        return image_pushed_time

    def _get_latest_images_of_repository_production(self, ecr_repository):
        logging.info(f"Obtaining latest docker image of repository {ecr_repository} for production environment")
        docker_images = self._client.list_images(
            repositoryName=ecr_repository,
        )
        images_of_environment = []
        cont = True
        while cont:
            for image in docker_images["imageIds"]:
                image_tag = image.get("imageTag", None)
                if image_tag:
                    image_tag_split = image_tag.split("-")
                    if len(image_tag_split) == 1:
                        if "latest" not in image_tag:
                            images_of_environment.append(
                                {
                                    "imageTag": image_tag,
                                    "imagePushedAt": self._obtain_image_pushed_time(ecr_repository, image_tag),
                                }
                            )
            if "nextToken" in docker_images:
                next_token = docker_images["nextToken"]
                docker_images = self._client.list_images(repositoryName=ecr_repository, nextToken=next_token)
            else:
                cont = False

        # This sorts semantic-release versions properly
        image_tags = [image["imageTag"] for image in images_of_environment]
        image_tags.sort(key=StrictVersion)

        if image_tags:
            latest_tag = image_tags[-1]
            latest_image = [image for image in images_of_environment if image["imageTag"] == latest_tag][0]

            return latest_image
        else:
            logging.error(f"There is no image in production environment for the repository {ecr_repository}")
            return None

    def _get_latest_image_of_repository_for_ephemeral_environment(self, environment, repository):
        images_of_environment = []
        logging.info(f"Obtaining latest Docker image in ECR repository {repository} for environment {environment}")
        docker_images = self._client.list_images(
            repositoryName=repository,
        )
        cont = True
        while cont:
            for image in docker_images["imageIds"]:
                image_tag = image.get("imageTag", None)
                if image_tag is not None:
                    image_tag_split = image_tag.split("-")
                    if len(image_tag_split) > 1:
                        image_tag_environment = image_tag_split[0]
                        if image_tag_environment == environment and "latest" not in image_tag:
                            images_of_environment.append(
                                {
                                    "imageTag": image_tag,
                                    "imagePushedAt": self._obtain_image_pushed_time(repository, image_tag),
                                }
                            )
            if "nextToken" in docker_images:
                next_token = docker_images["nextToken"]
                docker_images = self._client.list_images(repositoryName=repository, nextToken=next_token)
            else:
                cont = False
        return images_of_environment

    def _obtain_latest_image_of_repository_from_environment(self, environment, repository):
        latest_docker_images_in_repository = {}
        if environment != self._environment_id_production:
            images_of_environment = self._get_latest_image_of_repository_for_ephemeral_environment(
                environment, repository
            )
            if images_of_environment:
                images_of_environment.sort(key=lambda image: image["imageTag"].split("-")[1])
                latest_image_info = images_of_environment[-1]
                latest_docker_images_in_repository.update(
                    {
                        "repository": repository,
                        "image_tag": latest_image_info["imageTag"],
                        "imagePushedAt": latest_image_info["imagePushedAt"],
                    }
                )
        else:
            logging.info(f"Obtaining the newer image in the repository {repository} for the environment {environment}")
            latest_image_repository = self._get_latest_images_of_repository_production(repository)
            if latest_image_repository:
                latest_docker_images_in_repository.update(
                    {
                        "repository": repository,
                        "image_tag": latest_image_repository["imageTag"],
                        "imagePushedAt": latest_image_repository["imagePushedAt"],
                    }
                )
            else:
                logging.warning(f"No docker images found in repository {repository} for environment {environment}")
                # Create a new SES resource and specify a region.
                client = boto3.client("ses", region_name=AWS_REGION)

                # Try to send the email.
                try:
                    # Provide the contents of the email.
                    response = client.send_email(
                        Destination={
                            "ToAddresses": [
                                RECIPIENT,
                            ],
                        },
                        Message={
                            "Body": {
                                "Html": {
                                    "Charset": CHARSET,
                                    "Data": BODY_HTML,
                                },
                                "Text": {
                                    "Charset": CHARSET,
                                    "Data": BODY_TEXT,
                                },
                            },
                            "Subject": {
                                "Charset": CHARSET,
                                "Data": f"WARNING: Could not get the latest version of the {repository} repository",
                            },
                        },
                        Source=SENDER,
                    )
                # Display an error if something goes wrong.
                except ClientError as e:
                    print(e.response["Error"]["Message"])
                else:
                    print("Email sent! Message ID:"),
                    print(response["MessageId"])
        return latest_docker_images_in_repository

    def _obtain_latest_image_of_repositories_from_environment(self, environment, repositories):
        latest_docker_images_in_repositories = []
        for repository in repositories:
            latest_docker_image_for_repository = self._obtain_latest_image_of_repository_from_environment(
                environment, repository
            )
            latest_docker_images_in_repositories.append(latest_docker_image_for_repository)
        return latest_docker_images_in_repositories

    def _obtain_images_of_repository_from_environment_in_repository(self, environment, repository, all_images):
        images_of_environment = []
        logging.info(f"Obtaining oldest Docker images in ECR repository {repository}")
        docker_images = self._client.list_images(
            repositoryName=repository,
        )
        cont = True
        while cont:
            for image in docker_images["imageIds"]:
                image_tag = image.get("imageTag", None)
                if image_tag:
                    if all_images or ("latest" not in image_tag and not all_images):
                        image_tag_split = image_tag.split("-")
                        if (environment == self._environment_id_production and len(image_tag_split) == 1) or (
                            len(image_tag_split) == 2 and image_tag_split[0] == environment
                        ):
                            images_of_environment.append(
                                {
                                    "imageTag": image_tag,
                                    "imagePushedAt": self._obtain_image_pushed_time(repository, image_tag),
                                }
                            )
            if "nextToken" in docker_images:
                next_token = docker_images["nextToken"]
                docker_images = self._client.list_images(repositoryName=repository, nextToken=next_token)
            else:
                cont = False
        return images_of_environment

    def _obtain_images_to_delete_of_repositories_from_environment(self, environment, ecr_repositories, only_old):
        if len(ecr_repositories) > 1:
            logging.info(
                f'Obtaining oldest docker images of repositories {", ".join(ecr_repositories)} '
                f"for environment {environment}"
            )
        docker_images_in_repositories = []
        for repository in ecr_repositories:
            if only_old:
                images_of_environment = self._obtain_images_of_repository_from_environment_in_repository(
                    environment, repository, False
                )
            else:
                images_of_environment = self._obtain_images_of_repository_from_environment_in_repository(
                    environment, repository, True
                )
            if images_of_environment:
                if only_old and len(images_of_environment) > 2:
                    images_of_environment.sort(key=lambda image: image["imageTag"])
                    docker_images_in_repositories.append(
                        {
                            "repository": repository,
                            "images_to_delete": [i["imageTag"] for i in images_of_environment[:-2]],
                        }
                    )
                elif only_old and len(images_of_environment) <= 2:
                    logging.error(
                        f"Repository {repository} has {len(images_of_environment)} oldest images "
                        f"for environment {environment}. No image is going to be deleted"
                    )
                else:
                    images_of_environment.sort(key=lambda image: image["imageTag"])
                    docker_images_in_repositories.append(
                        {"repository": repository, "images_to_delete": [i["imageTag"] for i in images_of_environment]}
                    )
            else:
                logging.error(
                    f"Repository {repository} hasn't images "
                    f"for environment {environment}. No image is going to be deleted"
                )
        return ecr_repositories, docker_images_in_repositories

    def _delete_images_in_batches(self, repositories_to_delete_images, docker_images_to_delete_in_repositories):
        logging.info(
            f"The number of images that are going to be deleted for the repository/repositories "
            f"{','.join(repositories_to_delete_images)} is "
            f"{self._calculate_number_of_images_to_delete(docker_images_to_delete_in_repositories)}"
        )
        for repository in docker_images_to_delete_in_repositories:
            repository_name = repository["repository"]
            logging.info(f"The older images of the ECR repository {repository_name} are going to be deleted")
            images_to_delete = repository["images_to_delete"]
            for i in range(0, len(images_to_delete), 100):
                images_to_delete_chunk = images_to_delete[i : i + 100]
                logging.info(
                    f"Deleting from repository {repository_name} the image with tags "
                    f'{",".join(map(str, images_to_delete_chunk))}'
                )
                response = self._client.batch_delete_image(
                    repositoryName=repository_name, imageIds=[{"imageTag": str(id_)} for id_ in images_to_delete_chunk]
                )
                if len(response["failures"]) > 0:
                    logging.error("The following errors have occurred during image deletion")
                    for failure in response["failures"]:
                        logging.error(f"{failure}")
                else:
                    logging.info("The images have been successfully deleted")

    def _delete_images_in_ecr_repositories(self, environment, repository):
        if environment:
            all_repositories = parser.parse_args().all_repositories
            ecr_repositories = []
            if all_repositories:
                ecr_repositories = self._get_all_ecr_repositories_from_aws()
            elif repository:
                ecr_repositories.append(repository)
            else:
                logging.error("It's necessary provide a repository or provide -a/--all flag")
                exit(1)
            if parser.parse_args().oldest_images:
                (
                    repositories_to_delete_images,
                    docker_images_to_delete_in_repositories,
                ) = self._obtain_images_to_delete_of_repositories_from_environment(environment, ecr_repositories, True)
            else:
                (
                    repositories_to_delete_images,
                    docker_images_to_delete_in_repositories,
                ) = self._obtain_images_to_delete_of_repositories_from_environment(environment, ecr_repositories, False)
            if docker_images_to_delete_in_repositories:
                self._delete_images_in_batches(repositories_to_delete_images, docker_images_to_delete_in_repositories)
            else:
                logging.info("There aren't Docker images to delete")
        else:
            logging.error("It's necessary provide an environment where are going to delete docker images")
            exit(1)

    def _print_results(self, latest_images_for_ecr_repositories, print_results, environment, get_all):
        if latest_images_for_ecr_repositories and print_results:
            self._write_to_json_file("latest_images_for_ecr_repositories", latest_images_for_ecr_repositories)
            if print_results:
                if get_all:
                    for images_for_ecr_repository in latest_images_for_ecr_repositories:
                        repository = images_for_ecr_repository.get("repository")
                        logging.info(
                            f"The result of obtaining the latest docker images for the repository "
                            f"{repository} in environment {environment} is the following"
                        )
                        print(f"{json.dumps(images_for_ecr_repository, indent=4, default=str)}")
                else:
                    repository = latest_images_for_ecr_repositories.get("repository")
                    logging.info(
                        f"The result of obtaining the latest docker images for the repository "
                        f"{repository} in environment {environment} is the following"
                    )
                    print(f"{json.dumps(latest_images_for_ecr_repositories, indent=4, default=str)}")

    def do_necessary_actions(self):
        if parser.parse_args().delete or parser.parse_args().get:
            environment = parser.parse_args().environment
            repository = parser.parse_args().repository
            all_repositories = parser.parse_args().all_repositories
            if parser.parse_args().delete:
                self._delete_images_in_ecr_repositories(environment, repository)
            elif parser.parse_args().get:
                if all_repositories:
                    repositories = self._get_all_ecr_repositories_from_aws()
                    latest_images_from_ecr_repositories = self._obtain_latest_image_of_repositories_from_environment(
                        environment, repositories
                    )
                else:
                    logging.info(
                        f"It's going to obtain images for repository {repository} in environment {environment}"
                    )
                    latest_images_from_ecr_repositories = self._obtain_latest_image_of_repository_from_environment(
                        environment, repository
                    )
                self._print_results(
                    latest_images_from_ecr_repositories,
                    parser.parse_args().print_results,
                    environment,
                    all_repositories,
                )
        else:
            logging.error("The only valid options are -g/--get or -d/--delete")
            exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        dest="delete",
        action="store_true",
        help="Boolean flag to indicate whether deleting actions are to be performed on ECR repositories",
        required=False,
        default=False,
    )
    parser.add_argument(
        "-g",
        dest="get",
        action="store_true",
        help="Boolean flag to get latest image on ECR repositories",
        required=False,
        default=False,
    )
    parser.add_argument(
        "-r", "--repository", type=str, help="Name of the Docker ECR repository to obtain images", required=False
    )
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        help="Flag to indicate the file path where " "the information of the environments actually deployed",
        default="/tmp/latest_images_for_ecr_repositories.json",
        required=False,
    )
    parser.add_argument("-e", "--environment", type=str, help="Name of the environment to get images", required=True)
    parser.add_argument(
        "-p",
        dest="print_results",
        action="store_true",
        help="Flag to indicate whether the results are to be printed on the screen",
        required=False,
        default=False,
    )
    parser.add_argument(
        "-a",
        dest="all_repositories",
        action="store_true",
        help="Indicate if all ECR repositories are going to be explored to delete older images",
        required=False,
        default=False,
    )
    parser.add_argument(
        "-o",
        dest="oldest_images",
        action="store_true",
        help="Indicate oldest images is going to be deleted (leaving two always)",
        required=False,
        default=False,
    )
    ecr_util = EcrUtil()
    ecr_util.do_necessary_actions()

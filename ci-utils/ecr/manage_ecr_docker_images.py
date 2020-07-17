#!/usr/bin/env python3

import argparse
import os
import logging
import json
import boto3
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)


class EcrUtil:
    _client = boto3.client('ecr', region_name='us-east-1')
    _repositories_to_avoid = ['automation-python-3.6', 'automation-python-3.6-alpine']
    _production_tag = "automation-master"

    @staticmethod
    def _write_to_json_file(filename, content):
        filepath = f"/tmp/{filename}.json"
        with open(filepath, 'w+') as f:
            f.write(json.dumps(content, indent=4, default=str))
        return filepath

    def _get_all_ecr_repositories_from_aws(self):
        repositories_in_ecr = []
        repositories = self._client.describe_repositories()
        for repository in repositories['repositories']:
            if 'automation' in repository['repositoryName']:
                repositories_in_ecr.append(repository['repositoryName'])
        if len(repositories_in_ecr) > 0:
            repositories_to_avoid = self._repositories_to_avoid
            repositories_in_ecr = [elem for elem in repositories_in_ecr if elem not in repositories_to_avoid]
        return repositories_in_ecr

    def _get_ecr_repositories(self):
        ecr_repositories = []
        if parser.parse_args().all_repositories:
            ecr_repositories = self._get_all_ecr_repositories_from_aws()
        else:
            repository = parser.parse_args().repository
            if parser.parse_args().repository is None:
                logging.error("No value specified for repository")
                exit(1)
            ecr_repositories.append(repository)
        return ecr_repositories

    @staticmethod
    def _calculate_number_of_images_to_delete(docker_images_to_delete_in_repositories):
        total_images_to_delete = 0
        for repository in docker_images_to_delete_in_repositories:
            total_images_to_delete += len(repository['images_to_delete'])
        return total_images_to_delete

    def _get_ecr_images_to_delete_from_environment(self, environment, repositories_to_delete_images):
        docker_images_to_delete_in_repositories = []
        for repository in repositories_to_delete_images:
            images_to_delete_in_repository = []
            logging.info(f"Obtaining Docker images in ECR repository {repository}")
            docker_images = self._client.list_images(
                repositoryName=repository,
            )
            cont = True
            while cont:
                for image in docker_images['imageIds']:
                    image_tag = image.get('imageTag', None)
                    if image_tag is not None:
                        image_tag_environment = "-".join(image_tag.split("-")[0:2])
                        if image_tag_environment == environment:
                            images_to_delete_in_repository.append(image_tag)
                if 'nextToken' in docker_images:
                    next_token = docker_images['nextToken']
                    docker_images = self._client.list_images(
                        repositoryName=repository,
                        nextToken=next_token
                    )
                else:
                    cont = False
            if images_to_delete_in_repository:
                docker_images_to_delete_in_repositories.append(
                    {
                        'repository': repository,
                        'images_to_delete': images_to_delete_in_repository
                    }
                )
        return repositories_to_delete_images, docker_images_to_delete_in_repositories

    @staticmethod
    def _get_environments_deployed_from_file(environments_file):
        with open(environments_file, "r") as f:
            environments_from_mr_opened = json.load(f)
        environments_deployed = []
        for environment in environments_from_mr_opened:
            if environment['is_deployed']:
                environments_deployed.append(environment['environment'])
        return environments_deployed

    def _get_ecr_images_to_delete_from_environments_not_deployed(self, environments_file,
                                                                 repositories_to_delete_images):
        environments_deployed = self._get_environments_deployed_from_file(environments_file)
        logging.info(f'The environments actually deployed are the following: {", ".join(environments_deployed)}')
        if environments_deployed:
            docker_images_to_delete_in_repositories = []
            for repository in repositories_to_delete_images:
                images_to_delete_in_repository = []
                logging.info(f"Obtaining Docker images in ECR repository {repository}")
                docker_images = self._client.list_images(
                    repositoryName=repository,
                )
                cont = True
                while cont:
                    for image in docker_images['imageIds']:
                        image_tag = image.get('imageTag', None)
                        if image_tag is not None:
                            image_tag_environment = "-".join(image_tag.split("-")[0:2])
                            if image_tag_environment not in environments_deployed:
                                images_to_delete_in_repository.append(image_tag)
                    if 'nextToken' in docker_images:
                        next_token = docker_images['nextToken']
                        docker_images = self._client.list_images(
                            repositoryName=repository,
                            nextToken=next_token
                        )
                    else:
                        cont = False
                if images_to_delete_in_repository:
                    docker_images_to_delete_in_repositories.append(
                        {
                            'repository': repository,
                            'images_to_delete': images_to_delete_in_repository
                        }
                    )
                else:
                    logging.info(f"There aren't images to delete in repository {repository}")
            return repositories_to_delete_images, docker_images_to_delete_in_repositories
        else:
            logging.error("There isn't any environment deployed")
            exit(0)

    def _obtain_oldest_images_of_repositories_from_environment(self, environment, ecr_repositories):
        logging.info(f'Obtaining oldest docker images of repositories {", ".join(ecr_repositories)} '
                     f'for environment {environment}')
        oldest_docker_images_in_repositories = []
        for repository in ecr_repositories:
            oldest_images_of_environment = []
            logging.info(f"Obtaining oldest Docker image in ECR repository {repository}")
            docker_images = self._client.list_images(
                repositoryName=repository,
            )
            cont = True
            while cont:
                for image in docker_images['imageIds']:
                    image_tag = image.get('imageTag', None)
                    if image_tag:
                        image_tag_environment = "-".join(image_tag.split("-")[0:2])
                        if image_tag_environment == environment:
                            oldest_images_of_environment.append(
                                {
                                    'imageTag': image_tag,
                                    'imagePushedAt': self._obtain_image_pushed_time(repository, image_tag)
                                }
                            )
                if 'nextToken' in docker_images:
                    next_token = docker_images['nextToken']
                    docker_images = self._client.list_images(
                        repositoryName=repository,
                        nextToken=next_token
                    )
                else:
                    cont = False
            if len(oldest_images_of_environment) > 2:
                oldest_images_of_environment.sort(key=lambda image: image["imagePushedAt"])
                oldest_docker_images_in_repositories.append(
                    {
                        'repository': repository,
                        'images_to_delete': [i['imageTag'] for i in oldest_images_of_environment[:-2]]
                    }
                )
            else:
                oldest_images_of_environment.sort(key=lambda image: image["imagePushedAt"])
                logging.error(f"Repository {repository} has {len(oldest_images_of_environment)} images "
                              f"for environment {environment}. No image is going to be deleted")
        return ecr_repositories, oldest_docker_images_in_repositories

    def _delete_images_in_ecr_repositories(self, environment, ecr_repositories):
        environments_file = parser.parse_args().file
        if environment or environments_file:
            if environment:
                if parser.parse_args().oldest_images:
                    repositories_to_delete_images, docker_images_to_delete_in_repositories = self.\
                        _obtain_oldest_images_of_repositories_from_environment(environment,
                                                                               ecr_repositories)
                else:
                    repositories_to_delete_images, docker_images_to_delete_in_repositories = \
                            self._get_ecr_images_to_delete_from_environment(environment, ecr_repositories)
            elif environments_file:
                repositories_to_delete_images, docker_images_to_delete_in_repositories = \
                    self._get_ecr_images_to_delete_from_environments_not_deployed(environments_file,
                                                                                  ecr_repositories)
            if docker_images_to_delete_in_repositories:
                self._delete_images_in_batches(repositories_to_delete_images, docker_images_to_delete_in_repositories)
            else:
                logging.info("There aren't Docker images to delete")
        else:
            logging.error("It's necessary provide an environment or a file with information "
                          "about deployed environments")
            exit(1)

    def _delete_images_in_batches(self, repositories_to_delete_images, docker_images_to_delete_in_repositories):
        logging.info(f"The number of images that are going to be deleted for the repository/repositories "
                     f"{','.join(repositories_to_delete_images)} is "
                     f"{self._calculate_number_of_images_to_delete(docker_images_to_delete_in_repositories)}")
        for repository in docker_images_to_delete_in_repositories:
            repository_name = repository['repository']
            logging.info(f"The older images of the ECR repository {repository_name} are going to be deleted")
            images_to_delete = repository['images_to_delete']
            for i in range(0, len(images_to_delete), 100):
                images_to_delete_chunk = images_to_delete[i:i + 100]
                logging.info(f'Deleting from repository {repository_name} the image with tags '
                             f'{",".join(map(str, images_to_delete_chunk))}')
                response = self._client.batch_delete_image(
                    repositoryName=repository_name,
                    imageIds=[{'imageTag': str(id_)} for id_ in images_to_delete_chunk]
                )
                if len(response['failures']) > 0:
                    logging.error("The following errors have occurred during image deletion")
                    for failure in response['failures']:
                        logging.error(f"{failure}")
                else:
                    logging.info("The images have been successfully deleted")

    def _obtain_image_pushed_time(self, repository_name, image_tag):
        image_pushed_time = None
        logging.info(f"Obtaining push time of Docker image with tag {image_tag} in repository {repository_name}")
        response = self._client.describe_images(
            repositoryName=repository_name,
            imageIds=[
                {
                    'imageTag': image_tag
                },
            ],
        )
        if response['imageDetails']:
            image_pushed_time = response['imageDetails'][0]['imagePushedAt']
        return image_pushed_time

    def _get_latest_images_of_repository_production(self, ecr_repository):
        logging.info(f"Obtaining latest docker image of repository {ecr_repository} for production environment")
        docker_images = self._client.list_images(
            repositoryName=ecr_repository,
        )
        images_of_environment = []
        cont = True
        while cont:
            for image in docker_images['imageIds']:
                image_tag = image.get('imageTag', None)
                if image_tag:
                    image_tag_environment = "-".join(image_tag.split("-")[0:2])
                    if image_tag_environment == self._production_tag and 'latest' not in image_tag:
                        images_of_environment.append(
                            {
                                'imageTag': image_tag,
                                'imagePushedAt': self._obtain_image_pushed_time(ecr_repository, image_tag)
                            }
                        )
            if 'nextToken' in docker_images:
                next_token = docker_images['nextToken']
                docker_images = self._client.list_images(
                    repositoryName=ecr_repository,
                    nextToken=next_token
                )
            else:
                cont = False
        images_of_environment.sort(key=lambda image: image["imagePushedAt"])
        if images_of_environment:
            return images_of_environment[-1]
        else:
            logging.error(f"There is no image in production environment for the repository {ecr_repository}")
            exit(1)

    def _obtain_latest_images_of_repositories_from_environment(self, environment, ecr_repositories):
        logging.info(f'Obtaining latest docker images of repositories {", ".join(ecr_repositories)} '
                     f'for environment {environment}')
        latest_docker_images_in_repositories = []
        for repository in ecr_repositories:
            images_of_environment = []
            logging.info(f"Obtaining latest Docker image in ECR repository {repository}")
            docker_images = self._client.list_images(
                repositoryName=repository,
            )
            cont = True
            while cont:
                for image in docker_images['imageIds']:
                    image_tag = image.get('imageTag', None)
                    if image_tag is not None:
                        image_tag_environment = "-".join(image_tag.split("-")[0:2])
                        if image_tag_environment == environment and 'latest' not in image_tag:
                            images_of_environment.append(
                                {
                                    'imageTag': image_tag,
                                    'imagePushedAt': self._obtain_image_pushed_time(repository, image_tag)
                                }
                            )
                if 'nextToken' in docker_images:
                    next_token = docker_images['nextToken']
                    docker_images = self._client.list_images(
                        repositoryName=repository,
                        nextToken=next_token
                    )
                else:
                    cont = False
            if images_of_environment:
                images_of_environment.sort(key=lambda image: image["imagePushedAt"])
                latest_image_info = images_of_environment[-1]
                latest_docker_images_in_repositories.append(
                    {
                        'repository': repository,
                        'image_tag': latest_image_info['imageTag'],
                        'imagePushedAt': latest_image_info['imagePushedAt']
                    }
                )
            else:
                logging.error(f"There isn't a newer image in the repository {repository} for the environment "
                              f"{environment}. Assigning latest from master")
                latest_image_repository = self._get_latest_images_of_repository_production(repository)
                latest_docker_images_in_repositories.append(
                    {
                        'repository': repository,
                        'image_tag': latest_image_repository['imageTag'],
                        'imagePushedAt': latest_image_repository['imagePushedAt']
                    }
                )
        return ecr_repositories, latest_docker_images_in_repositories, environment

    def _print_results(self, latest_images_for_ecr_repositories, print_results, repositories, environment):
        if latest_images_for_ecr_repositories and print_results:
            self._write_to_json_file('latest_images_for_ecr_repositories', latest_images_for_ecr_repositories)
            logging.info(f'The result of obtaining the latest docker images for the repositories '
                         f'{", ".join(repositories)} in environment {environment} is the following')
            print(f"{json.dumps(latest_images_for_ecr_repositories, indent=4, default=str)}")

    def do_necessary_actions(self):
        if parser.parse_args().delete or parser.parse_args().get:
            environment = parser.parse_args().environment
            ecr_repositories = self._get_ecr_repositories()
            if parser.parse_args().delete:
                self._delete_images_in_ecr_repositories(environment,
                                                        ecr_repositories)
            elif parser.parse_args().get:
                repositories, latest_images_for_ecr_repositories, environment = self.\
                    _obtain_latest_images_of_repositories_from_environment(environment,
                                                                           ecr_repositories)
                self._print_results(latest_images_for_ecr_repositories,
                                    parser.parse_args().print_results,
                                    repositories, environment)
        else:
            logging.error("The only valid options are -o/--obtain or -d/--delete")
            exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--delete',
                        type=bool,
                        help='Boolean flag to indicate whether deleting actions are to be '
                             'performed on ECR repositories',
                        required=False,
                        default=False)
    parser.add_argument('-g', '--get',
                        type=bool,
                        help='Boolean flag to get latest image on ECR repositories',
                        required=False,
                        default=False)
    parser.add_argument('-r', '--repository',
                        type=str,
                        help='Name of the Docker ECR repository to obtain images',
                        required=False)
    parser.add_argument('-f', '--file',
                        type=str,
                        help='flag to indicate the file path where '
                             'the information of the environments actually deployed',
                        required=False)
    parser.add_argument('-e', '--environment',
                        type=str,
                        help='Name of the environment to delete images',
                        required=True)
    parser.add_argument('-a', '--all_repositories',
                        type=bool,
                        help='Indicate if all ECR repositories are going to be explored to delete older images',
                        required=False,
                        default=False)
    parser.add_argument('-o', '--oldest_images',
                        type=bool,
                        help='Indicate oldest images is going to be deleted (leaving two always)',
                        required=False,
                        default=False)
    parser.add_argument('-p', '--print_results',
                        type=bool,
                        help='Flag to indicate whether the results are to be printed on the screen',
                        required=False,
                        default=False)
    ecr_util = EcrUtil()
    ecr_util.do_necessary_actions()

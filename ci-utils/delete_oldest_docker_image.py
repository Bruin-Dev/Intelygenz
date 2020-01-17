import subprocess
import os
import json
import logging
import sys

logging.basicConfig(level=logging.INFO)

FNULL = open(os.devnull, 'w')


class DeleteOlderDockerImage:
    def delete_oldest_image(self, repository_name_p):
        oldest_image_for_repository = self._get_oldest_image(repository_name_p)
        oldest_image_for_repository_image_tag = oldest_image_for_repository['imageTag']
        logging.info(f"Docker image for the ECR repository with name {repository_name_p} and imageTag "
                     f"{oldest_image_for_repository_image_tag} it's going to be deleted")
        delete_oldest_image_for_repository_exit_code = subprocess.call(
            ['aws', 'ecr', 'batch-delete-image', '--repository-name', repository_name_p,
             '--image-ids', 'imageTag=' + oldest_image_for_repository_image_tag,
             '--region', 'us-east-1'], stdout=FNULL)
        if delete_oldest_image_for_repository_exit_code != 0:
            logging.error(f"There were problems deleting docker image for the ECR repository with "
                          f"name {repository_name_p} and imageTag {oldest_image_for_repository_image_tag}")
        else:
            logging.info(f"Docker image for the ECR repository with "
                         f"name {repository_name_p} and imageTag {oldest_image_for_repository_image_tag} "
                         f"was successfully deleted")

    @staticmethod
    def _get_oldest_image(repository_name_p):
        logging.info(f"Getting all docker images for the ECR repository with name {repository_name_p}")
        get_all_images_for_repository = subprocess.Popen(['aws', 'ecr', 'list-images', '--repository-name',
                                                          repository_name_p, '--region', 'us-east-1'],
                                                         stdout=subprocess.PIPE)
        get_all_images_for_repository_output = json.loads(
            get_all_images_for_repository.stdout.read())['imageIds']
        num_of_images_for_repository = len(get_all_images_for_repository_output)
        logging.info(f"ECR repository with name {repository_name_p} has {num_of_images_for_repository} docker images")
        if num_of_images_for_repository > 0:
            get_all_images_for_repository_output.sort(key=lambda i: i['imageTag'])
            repository_oldest_image = get_all_images_for_repository_output[0]
            logging.info(f"The oldest docker image for the ECR repository with name {repository_name_p} "
                         f"has the following attributes {repository_oldest_image}")
            return repository_oldest_image
        else:
            logging.error(f"No docker images were found for the ECR repository with name {repository_name_p}")
            sys.exit(1)

    @staticmethod
    def print_usage():
        print("delete_oldest_docker_image -r <repository_name>")


if __name__ == '__main__':
    delete_older_docker_image_instance = DeleteOlderDockerImage()
    if sys.argv[0] == '-r':
        repository_name = sys.argv[1]
    elif sys.argv[1] == '-r':
        repository_name = sys.argv[2]
    else:
        delete_older_docker_image_instance.print_usage()
        sys.exit(1)

    repository_name_for_project = 'automation-' + repository_name
    delete_older_docker_image_instance.delete_oldest_image(repository_name_for_project)

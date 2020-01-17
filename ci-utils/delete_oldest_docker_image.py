import subprocess
import os
import json
import logging
import sys
from datetime import datetime

logging.basicConfig(level=logging.INFO)

FNULL = open(os.devnull, 'w')


class DeleteOlderDockerImage:
    def delete_oldest_image(self, repository_name_p):
        oldest_image_for_repository = self._get_oldest_image(repository_name_p)
        oldest_image_for_repository_image_digest = oldest_image_for_repository['imageDigest']
        oldest_image_for_repository_image_pushed_date = oldest_image_for_repository['imagePushedAt']
        logging.info(f"Docker image for the ECR repository {repository_name_p} with imageDigest "
                     f"{oldest_image_for_repository_image_digest} and pushed at "
                     f"{oldest_image_for_repository_image_pushed_date} it's going to be deleted")
        delete_oldest_image_for_repository_exit_code = subprocess.call(
            ['aws', 'ecr', 'batch-delete-image', '--repository-name', repository_name_p,
             '--image-ids', 'imageDigest=' + oldest_image_for_repository_image_digest,
             '--region', 'us-east-1'], stdout=FNULL)
        if delete_oldest_image_for_repository_exit_code != 0:
            logging.error(f"There were problems deleting docker image for the ECR repository "
                          f"{repository_name_p} with imageDigest {oldest_image_for_repository_image_digest}"
                          f" and pushed at {oldest_image_for_repository_image_pushed_date}")
        else:
            logging.info(f"Docker image for the ECR repository {repository_name_p} with imageDigest "
                         f"{oldest_image_for_repository_image_digest} and pushed at "
                         f"{oldest_image_for_repository_image_pushed_date} was successfully deleted")

    def _get_oldest_image(self, repository_name_p):
        logging.info(f"Getting all docker images for the ECR repository {repository_name_p}")
        get_all_images_for_repository = self._get_all_images_for_repository(repository_name_p)
        num_of_images_for_repository = len(get_all_images_for_repository)
        logging.info(f"ECR repository {repository_name_p} has {num_of_images_for_repository} docker images")
        if num_of_images_for_repository > 0:
            repository_oldest_image = get_all_images_for_repository[0]
            repository_oldest_image_date = self._convert_timestamp_to_date(
                repository_oldest_image['imagePushedAt'])
            logging.info(f"The oldest docker image for the ECR repository {repository_name_p} "
                         f"has imageDigest {repository_oldest_image['imageDigest']} and was pushed "
                         f"at {repository_oldest_image_date}")
            return {'imageDigest': repository_oldest_image['imageDigest'],
                    'imagePushedAt': repository_oldest_image_date}
        else:
            logging.error(f"No docker images were found for the ECR repository {repository_name_p}")
            sys.exit(1)

    @staticmethod
    def _get_all_images_for_repository(repository_name_p):
        get_all_images_for_repository_call = subprocess.Popen(["aws", "ecr", "describe-images", "--repository-name",
                                                               repository_name_p, "--region", "us-east-1",
                                                               "--query", "sort_by(imageDetails,& imagePushedAt)[*]"],
                                                              stdout=subprocess.PIPE)
        get_all_images_for_repository_call_output = json.loads(
            get_all_images_for_repository_call.stdout.read())
        return get_all_images_for_repository_call_output

    @staticmethod
    def _convert_timestamp_to_date(timestamp_p):
        return datetime.utcfromtimestamp(timestamp_p).strftime('%Y-%m-%d %H:%M:%S')

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

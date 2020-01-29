import subprocess
import os
import json
import logging
import sys
from datetime import datetime

ENVIRONMENT = os.environ.get("ENVIRONMENT_VAR")

logging.basicConfig(level=logging.INFO)

FNULL = open(os.devnull, 'w')


class DeleteOlderDockerImage:
    _default_repositories = ['automation-bruin-bridge',
                             'automation-last-contact-report',
                             'automation-metrics-dashboard/grafana',
                             'automation-metrics-dashboard/prometheus',
                             'automation-metrics-dashboard/thanos',
                             'automation-metrics-dashboard/thanos-querier',
                             'automation-metrics-dashboard/thanos-store-gateway',
                             'automation-nats-server',
                             'automation-notifier',
                             'automation-service-affecting-monitor',
                             'automation-service-outage-monitor',
                             'automation-service-outage-triage',
                             'automation-sites-monitor',
                             'automation-t7-bridge',
                             'automation-velocloud-bridge']

    def get_all_newer_images_and_save_in_json_file(self):
        for repository in self._default_repositories:
            self._get_newer_image(repository)

    def _get_newer_image(self, repository_name_p):
        newer_image = self._get_one_image_of_all_images_ordered_by_pushed_timestamp(repository_name_p, -1)
        data_newer_image = {}
        if newer_image['has_images']:
            logging.info(f"The newer docker image for the ECR repository {repository_name_p} and environment "
                         f"{ENVIRONMENT} has imageDigest {newer_image['imageDigest']} and was pushed "
                         f"at {newer_image['imagePushedAt']}")
            for tag in newer_image['imageTags']:
                if tag.split("-")[2] != "latest":
                    data_newer_image['tag'] = tag
        if not data_newer_image:
            logging.info(f"There isn't a newer image for the ECR repository {repository_name_p} and environment "
                         f"{ENVIRONMENT}. It's going to be used latest stable upload to production environment")
            data_newer_image['tag'] = "automation-master-latest"
        self._save_repository_name_newer_image(repository_name_p, data_newer_image)

    @staticmethod
    def _save_repository_name_newer_image(repository_name_p, data_newer_image):
        if '/' in repository_name_p:
            with open(repository_name_p.split('/')[1] + '.json', 'w') as outfile:
                json.dump(data_newer_image, outfile)
        else:
            with open(repository_name_p + '.json', 'w') as outfile:
                json.dump(data_newer_image, outfile)

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
        oldest_image = self._get_one_image_of_all_images_ordered_by_pushed_timestamp(repository_name_p, 0)
        if oldest_image['has_images']:
            logging.info(f"The oldest docker image for the ECR repository {repository_name_p} "
                         f"has imageDigest {oldest_image['imageDigest']} and was pushed "
                         f"at {oldest_image['imagePushedAt']}")
            return oldest_image
        else:
            logging.info(f"There isn't an older image for repository {repository_name_p} and environment {ENVIRONMENT}")
            sys.exit(0)

    def _get_one_image_of_all_images_ordered_by_pushed_timestamp(self, repository_name_p, pos):
        images_of_environment_ordered = {'has_images': False}
        logging.info(f"Getting all docker images for the ECR repository {repository_name_p}")
        get_all_images_for_repository = self._get_all_images_for_repository_of_environment(repository_name_p)
        num_of_images_for_repository = len(get_all_images_for_repository)
        if num_of_images_for_repository > 0:
            logging.info(f"ECR repository {repository_name_p} has {num_of_images_for_repository} docker images "
                         f"for environment {ENVIRONMENT}")
            repository_image = get_all_images_for_repository[pos]
            repository_image_date = self._convert_timestamp_to_date(
                repository_image['imagePushedAt'])
            images_of_environment_ordered.update({'imageDigest': repository_image['imageDigest'],
                                                  'imagePushedAt': repository_image_date,
                                                  'imageTags': repository_image['imageTags'],
                                                  'has_images': True})
        else:
            logging.error(f"No docker images were found for the ECR repository {repository_name_p} "
                          f"and the environment {ENVIRONMENT}")
        return images_of_environment_ordered

    @staticmethod
    def _get_all_images_for_repository_of_environment(repository_name_p):
        get_all_images_for_repository_call = subprocess.Popen(["aws", "ecr", "describe-images", "--repository-name",
                                                               repository_name_p, "--region", "us-east-1",
                                                               "--query", "sort_by(imageDetails,& imagePushedAt)[*]"],
                                                              stdout=subprocess.PIPE)
        get_all_images_for_repository_call_output = json.loads(
            get_all_images_for_repository_call.stdout.read())
        images_for_environment = []
        for element in get_all_images_for_repository_call_output:
            if 'imageTags' in element:
                for tag in element['imageTags']:
                    if str(ENVIRONMENT) in tag:
                        images_for_environment.append(element)
        return images_for_environment

    @staticmethod
    def _convert_timestamp_to_date(timestamp_p):
        return datetime.utcfromtimestamp(timestamp_p).strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def print_usage():
        print("delete_oldest_docker_image -r <repository_name>")


if __name__ == '__main__':
    delete_older_docker_image_instance = DeleteOlderDockerImage()
    get_all_images = False
    if sys.argv[0] == '-g' or sys.argv[1] == '-g':
        get_all_images = True
        delete_older_docker_image_instance.get_all_newer_images_and_save_in_json_file()
    elif sys.argv[0] == '-r':
        repository_name = sys.argv[1]
    elif sys.argv[1] == '-r':
        repository_name = sys.argv[2]
    else:
        delete_older_docker_image_instance.print_usage()
        sys.exit(1)
    if not get_all_images and repository_name:
        delete_older_docker_image_instance.delete_oldest_image(repository_name)

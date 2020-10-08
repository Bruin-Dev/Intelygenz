#!/usr/bin/env python3

import argparse

import requests
import os
import subprocess
import tarfile
import config
import json
from sys import exit


class PapertrailProvisioner:
    def __init__(self):
        self._papertrail_dashboard_config = config.PAPERTRAIL_PROVISIONING
        self._papertrail_cli_donwload_url = config.PAPERTRAIL_CLI_DONWLOAD_URL
        self._current_directory = os.getcwd()

    def _download_go_papertrail_cli(self):
        files = []
        directory = "/tmp/"
        filename = "papertrail_cli"
        file_download_directory = directory + filename
        print(f"Download papertrail cli in the directory {file_download_directory}")
        r = requests.get(self._papertrail_cli_donwload_url)
        with open(file_download_directory, 'wb') as f:
            f.write(r.content)
        tar = tarfile.open(file_download_directory)
        tar_files = tar.getnames()
        if len(tar_files) > 0:
            files = tar_files
            subprocess.call(['tar', '-zxf', file_download_directory, '-C', directory])
            subprocess.call(['rm', '-f', file_download_directory])
        else:
            exit(1)
        return files, directory

    @staticmethod
    def _delete_files(files, directory):
        for file in files:
            file_to_delete = directory + file
            print(f"Deleting file {file_to_delete}")
            subprocess.call(['rm', file_to_delete])

    @staticmethod
    def _get_build_number_query(repository):
        docker_images_file = parser.parse_args().docker_images_file
        with open(docker_images_file) as json_file:
            data = json.load(json_file)
        return [elem['image_tag'] for elem in data if elem['repository'] == repository][0].split("-")[-1]

    def papertrail_provision(self):
        file_exec = "go-papertrail-cli"
        go_papertrail_cli_files, directory = self._download_go_papertrail_cli()
        if file_exec in go_papertrail_cli_files:
            papertrail_cli_exec = directory + file_exec
            papertrail_groups_config = self._papertrail_dashboard_config
            if len(papertrail_groups_config["groups"]) > 0:
                for group in papertrail_groups_config["groups"]:
                    group_name = group['group_name']
                    wildcard = group['wildcard']
                    destination_port = group['destination_port']
                    system_type = group['system_type']
                    is_alarm_group = group.get('alarms', False)
                    is_notifications_group = group.get('notifications', False)
                    for search in group['searches']:
                        search_name = search['search_name']
                        query = search['query']
                        if not is_alarm_group and not is_notifications_group:
                            if "repository" in search:
                                repository = search['repository']
                                build_number = self._get_build_number_query(repository)
                                query = query.replace('<BUILD_NUMBER>', build_number)
                            subprocess.call([papertrail_cli_exec, '-a', 'd', '-g', group_name, '-w', wildcard, '-S',
                                             search_name, '-q', query, '-p', destination_port, '-t', system_type,
                                             '--delete-only-searches', 'true'])
                        subprocess.call([papertrail_cli_exec, '-a', 'c', '-g', group_name, '-w', wildcard, '-S',
                                         search_name, '-q', query, '-p', destination_port, '-t', system_type])
            self._delete_files(go_papertrail_cli_files, directory)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--docker_images_file',
                        type=str,
                        help='Flag to indicate where is stored the file '
                             'with information of docker images in ECR repositories',
                        required=True)
    papertrail_provisioner = PapertrailProvisioner()
    papertrail_provisioner.papertrail_provision()

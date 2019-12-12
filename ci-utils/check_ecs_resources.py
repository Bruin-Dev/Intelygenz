#!/bin/python

import os
import subprocess
import json
import logging
import sys
import re

logging.basicConfig(level=logging.INFO)

FNULL = open(os.devnull, 'w')
ENVIRONMENT = os.environ['TF_VAR_ENVIRONMENT']


class CheckECSResources:
    _total_ecs_tasks_allowed = 50

    def check_ecs_task_conditions(self):
        actual_tasks_deployed = self._check_ecs_clusters_tasks()
        tasks_to_be_deployed = self._get_tasks_to_deploy()
        total_ecs_tasks = self._calculate_total_ecs_tasks(actual_tasks_deployed, tasks_to_be_deployed)
        logging.info(f"The number of tasks to be deployed for the environment {ENVIRONMENT} is {tasks_to_be_deployed}")
        if total_ecs_tasks >= self._total_ecs_tasks_allowed:
            logging.error(f"The sum of actual ECS tasks deployed and ECS tasks to deploy in current environment is "
                          f"{total_ecs_tasks} that exceeds the maximum number allowed by AWS")
            logging.error("In order to deploy this environment, it will be necessary to delete one or "
                          "more ECS clusters")
            sys.exit(1)
        else:
            logging.info(f"The sum of actual ECS tasks deployed and ECS tasks to deploy current environment and "
                         f"maintain the others are {total_ecs_tasks} that not reach the limit of "
                         f"{self._total_ecs_tasks_allowed} tasks")

    @staticmethod
    def _calculate_total_ecs_tasks(actual_tasks_deployed, tasks_to_be_deployed):
        if actual_tasks_deployed['environment_already_deployed']:
            logging.info(f"The environment {ENVIRONMENT} was previously deployed in ECS with "
                         f"{actual_tasks_deployed['tasks_deployed_for_environment']} tasks")
            total_ecs_tasks = (
                    actual_tasks_deployed['total_task_ecs_clusters'] +
                    tasks_to_be_deployed -
                    actual_tasks_deployed['tasks_deployed_for_environment']
            )
        else:
            total_ecs_tasks = actual_tasks_deployed['total_task_ecs_clusters'] + tasks_to_be_deployed
        return total_ecs_tasks

    @staticmethod
    def _get_tasks_to_deploy():
        rootdir = os.getcwd()
        count_tasks = 0
        for folder, dirs, file in os.walk(rootdir):
            for files in file:
                if files.endswith('.tf'):
                    fullpath = open(os.path.join(folder, files), 'r')
                    count_services_file = 0
                    count_tasks_file = 0
                    for line in fullpath:
                        if "\"aws_ecs_service\"" in line:
                            count_services_file += 1
                        elif "desired_count" in line:
                            count_tasks_match = re.match(r'.*desired_count \= (?P<counter>\d+)$', line)
                            count_tasks_file = int(count_tasks_match.group('counter'))
                    count_tasks += count_tasks_file * count_services_file
        return count_tasks

    def _check_ecs_clusters_tasks(self):
        logging.info("It's going to be checked if there are enough resources to deploy a new ECS cluster in AWS")
        actual_clusters_arns = self._get_ecs_clusters_arns()
        if len(actual_clusters_arns) > 0:
            cluster_already_deployed = False
            if any(cluster_arn.split('/')[0] == ENVIRONMENT for cluster_arn in actual_clusters_arns):
                cluster_already_deployed = True
            logging.info(f"There are {len(actual_clusters_arns)} ECS cluster/s used by MetTel "
                         "Automation project in AWS")
            logging.info("The number of total tasks (pending and active) for the obtained ECS cluster/s will be "
                         "checked")
            total_tasks = self._get_total_tasks_for_ecs_clusters(actual_clusters_arns)
            logging.info(f"The number of total tasks (pending and active) for the ECS cluster/s are "
                         f"{total_tasks['total_task_ecs_clusters']}")
            return total_tasks
        else:
            logging.error("There aren't ECS clusters used by MetTel Automation project in AWS")
            sys.exit(1)

    @staticmethod
    def _get_ecs_clusters_arns():
        clusters_arns = []
        logging.info("Getting ARNs for ECS clusters used by MetTel Automation project in AWS")
        get_actual_clusters_call = subprocess.Popen(['aws', 'ecs', 'list-clusters', '--region', 'us-east-1'],
                                                    stdout=subprocess.PIPE, stderr=FNULL)
        try:
            actual_clusters = json.loads(get_actual_clusters_call.stdout.read())['clusterArns']
            if len(actual_clusters) > 0:
                for element in actual_clusters:
                    clusters_arns.append(element)
        except ValueError as e:
            logging.error("Problem occurring with command execution for list ECS clusters")
        return clusters_arns

    @staticmethod
    def _get_total_tasks_for_ecs_clusters(list_clusters_arn):
        environment_already_deployed = False
        total_task_ecs_clusters = 0
        tasks_deployed_for_environment = 0
        describe_clusters_command = ("aws ecs describe-clusters --cluster " + " ".join(list_clusters_arn) + " --region"
                                     + " us-east-1").split(" ")
        get_clusters_information_call = subprocess.Popen(describe_clusters_command, stdout=subprocess.PIPE)
        try:
            clusters_information = json.loads(get_clusters_information_call.stdout.read())
            if len(clusters_information['clusters']) > 0:
                for element in clusters_information['clusters']:
                    total_task_ecs_clusters += (element['runningTasksCount'] + element['pendingTasksCount'])
                    if element['clusterName'] == ENVIRONMENT:
                        environment_already_deployed = True
                        tasks_deployed_for_environment = element['runningTasksCount'] + element['pendingTasksCount']
        except ValueError as e:
            pass
        return {'total_task_ecs_clusters': total_task_ecs_clusters,
                'environment_already_deployed': environment_already_deployed,
                'tasks_deployed_for_environment': tasks_deployed_for_environment}


if __name__ == '__main__':
    check_ecs_services_instance = CheckECSResources()
    check_ecs_services_instance.check_ecs_task_conditions()

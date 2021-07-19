#!/bin/python

import os
import subprocess
import json
import logging
import sys

logging.basicConfig(level=logging.INFO)

FNULL = open(os.devnull, 'w')
ENVIRONMENT = os.environ['TF_VAR_ENVIRONMENT']


class CheckECSResources:
    _total_ecs_tasks_allowed = int(os.environ['ECS_MAX_TASKS'])
    _ecs_services_tasks = [os.environ['TF_VAR_bruin_bridge_desired_tasks'],
                           os.environ['TF_VAR_cts_bridge_desired_tasks'],
                           os.environ['TF_VAR_customer_cache_desired_tasks'],
                           os.environ['TF_VAR_digi_bridge_desired_tasks'],
                           os.environ['TF_VAR_digi_reboot_report_desired_tasks'],
                           os.environ['TF_VAR_dispatch_portal_backend_desired_tasks'],
                           os.environ['TF_VAR_dispatch_portal_frontend_desired_tasks'],
                           os.environ['TF_VAR_email_tagger_kre_bridge_desired_tasks'],
                           os.environ['TF_VAR_email_tagger_monitor_desired_tasks'],
                           os.environ['TF_VAR_hawkeye_affecting_monitor_desired_tasks'],
                           os.environ['TF_VAR_hawkeye_bridge_desired_tasks'],
                           os.environ['TF_VAR_hawkeye_customer_cache_desired_tasks'],
                           os.environ['TF_VAR_hawkeye_outage_monitor_desired_tasks'],
                           os.environ['TF_VAR_intermapper_outage_monitor_desired_tasks'],
                           os.environ['TF_VAR_last_contact_report_desired_tasks'],
                           os.environ['TF_VAR_links_metrics_api_desired_tasks'],
                           os.environ['TF_VAR_links_metrics_collector_desired_tasks'],
                           os.environ['TF_VAR_lit_bridge_desired_tasks'],
                           os.environ['TF_VAR_lumin_billing_report_desired_tasks'],
                           os.environ['TF_VAR_metrics_prometheus_desired_tasks'],
                           os.environ['TF_VAR_nats_server_desired_tasks'],
                           os.environ['TF_VAR_nats_server_1_desired_tasks'],
                           os.environ['TF_VAR_nats_server_2_desired_tasks'],
                           os.environ['TF_VAR_notifier_desired_tasks'],
                           os.environ['TF_VAR_service_affecting_monitor_desired_tasks'],
                           os.environ['TF_VAR_service_dispatch_monitor_desired_tasks'],
                           os.environ['TF_VAR_service_outage_monitor_1_desired_tasks'],
                           os.environ['TF_VAR_service_outage_monitor_2_desired_tasks'],
                           os.environ['TF_VAR_service_outage_monitor_3_desired_tasks'],
                           os.environ['TF_VAR_service_outage_monitor_4_desired_tasks'],
                           os.environ['TF_VAR_service_outage_monitor_triage_desired_tasks'],
                           os.environ['TF_VAR_sites_monitor_desired_tasks'],
                           os.environ['TF_VAR_t7_bridge_desired_tasks'],
                           os.environ['TF_VAR_ticket_collector_desired_tasks'],
                           os.environ['TF_VAR_ticket_statistics_desired_tasks'],
                           os.environ['TF_VAR_tnba_feedback_desired_tasks'],
                           os.environ['TF_VAR_tnba_monitor_desired_tasks'],
                           os.environ['TF_VAR_velocloud_bridge_desired_tasks']]

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
            num_total_task_ecs_clusters = actual_tasks_deployed['total_task_ecs_clusters']
            num_tasks_deployed_for_environment = actual_tasks_deployed['tasks_deployed_for_environment']
            total_ecs_tasks = num_total_task_ecs_clusters + tasks_to_be_deployed - num_tasks_deployed_for_environment
        else:
            total_ecs_tasks = actual_tasks_deployed['total_task_ecs_clusters'] + tasks_to_be_deployed
        return total_ecs_tasks

    def _get_tasks_to_deploy(self):
        return sum([int(t) for t in self._ecs_services_tasks if t is not None])

    def _check_ecs_clusters_tasks(self):
        logging.info("It's going to be checked if there are enough resources to deploy a new ECS cluster in AWS")
        actual_clusters_arns = self._get_ecs_clusters_arns()
        if len(actual_clusters_arns) > 0:
            logging.info(f"There are {len(actual_clusters_arns)} ECS cluster/s used by MetTel "
                         "Automation project in AWS")
            logging.info("The number of total tasks (pending and active) for the obtained ECS cluster/s will be "
                         "checked")
            total_tasks = self._get_total_tasks_for_ecs_clusters(actual_clusters_arns)
            logging.info(f"The number of total tasks (pending and active) for the ECS cluster/s are "
                         f"{total_tasks['total_task_ecs_clusters']}")
            return total_tasks
        else:
            logging.info("There aren't ECS clusters used by MetTel Automation project in AWS")
            sys.exit(0)

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
        cmd = f"aws ecs describe-clusters --cluster {' '.join(list_clusters_arn)} --region us-east-1"
        describe_clusters_command = (cmd.split(" "))
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

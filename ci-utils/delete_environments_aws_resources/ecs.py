#!/bin/python


import os
import subprocess
import json
import time
import logging

import common_utils as common_utils_module

logging.basicConfig(level=logging.INFO)

FNULL = open('/dev/null', 'w')


class EcsServices:
    @staticmethod
    def _delete_ecs_service(environment, service_name, service_id):
        logging.info(
            "Update desired count of service {} with id {} of ECS cluster {} to 0 ".format(service_name, service_id,
                                                                                           environment))
        subprocess.call(['aws', 'ecs', 'update-service', '--cluster', environment, '--service', service_id,
                         '--desired-count', '0'], stdout=FNULL)
        logging.info("Deleting service {} with id {} of cluster {}".format(service_name, service_id, environment))
        subprocess.call(['aws', 'ecs', 'delete-service', '--cluster', environment, '--service', service_id],
                        stdout=FNULL)

    def _stop_task_and_delete_services(self, environment):
        cmd_actual_task = "ecs-cli ps --cluster " + environment + " --desired-status RUNNING --region us-east-1"
        try:
            actual_tasks = subprocess.check_output([cmd_actual_task], shell=True)
            if actual_tasks is not None:
                logging.info("The tasks in execution of cluster {} will be interrupted".format(environment))
                result = actual_tasks.decode().splitlines()[1:]
                for element in result:
                    task_identifier = element.split('/')[0]
                    service_name = element.split('/')[1].split(' ')[0]
                    service_id = environment + '-' + service_name
                    self._delete_ecs_service(environment, service_name, service_id)
                    logging.info("Stopping task {} of service {}".format(task_identifier, service_name))
                    subprocess.call(['aws', 'ecs', 'stop-task', '--cluster', environment, '--task', task_identifier],
                                    stdout=FNULL)
        except subprocess.CalledProcessError as e:
            logging.error("Cluster {} doesn't have active running tasks".format(environment))
        self._list_and_delete_all_services(environment)

    def _list_and_delete_all_services(self, environment):
        actual_services_call = subprocess.Popen(['aws', 'ecs', 'list-services', '--cluster', environment, '--region',
                                                 'us-east-1'], stdout=subprocess.PIPE, stderr=FNULL)
        try:
            actual_services = json.loads(actual_services_call.stdout.read())
            if len(actual_services['serviceArns']) > 0:
                for element in actual_services['serviceArns']:
                    service_name = '-'.join(element.split('/')[1].split('-')[2:])
                    service_id = element.split('/')[1]
                    self._delete_ecs_service(environment, service_name, service_id)
            else:
                logging.error("There are no services associated with the cluster {}".format(environment))
        except ValueError as e:
            logging.error("There are no services associated with the cluster {}".format(environment))

    @staticmethod
    def _check_servicediscovery_namespace_exists(actual_namespaces, namespace_name):
        if any(namespaces['Name'] == namespace_name for namespaces in actual_namespaces['Namespaces']):
            return True
        else:
            return False

    @staticmethod
    def _get_servicediscovery_id(actual_namespaces_json, namespace_name):
        for element in actual_namespaces_json['Namespaces']:
            if element['Name'] == namespace_name:
                return element['Id']

    @staticmethod
    def _get_services_in_namespace(environment, namespace_id):
        services = []
        logging.info("Recovering services associated with namespace {}".format(namespace_id))
        servicediscovery_services_list_call = subprocess.Popen(
            ['aws', 'servicediscovery', 'list-services', '--region', 'us-east-1'], stdout=subprocess.PIPE)
        actual_services = json.loads(servicediscovery_services_list_call.stdout.read())
        for element in actual_services['Services']:
            if environment in element['Name']:
                services.append({"service_name": element['Name'], "service_id": element['Id']})
        return services

    @staticmethod
    def _delete_services_in_namespace(environment, services):
        if len(services) == 0:
            logging.info('There is no services to delete from environment {}'.format(environment))
        else:
            common_utils_instance = common_utils_module.CommonUtils()
            for index in range(len(services)):
                for key in services[index]:
                    logging.info(
                        "Deleting service with name {} and id {} from cluster {}".format(
                            services[index]["service_name"],
                            services[index]["service_id"],
                            environment))
                    remove_service_cmd = 'aws, servicediscovery, delete-service, --id, ' + services[index][
                        "service_id"] + ', --region, us-east-1'
                    remove_service_result = subprocess.call(remove_service_cmd.split(', '), stdout=FNULL)
                    common_utils_instance.check_current_state_call(remove_service_result,
                                                                   'Service from Service Discovery',
                                                                   services[index]["service_id"])
                    if remove_service_result != 0:
                        service_from_discovery_service_delete_try = 0
                        current_exit_code = 0
                        while common_utils_instance.can_retry_call(service_from_discovery_service_delete_try) and \
                                current_exit_code != 0:
                            current_exit_code, service_from_discovery_service_delete_try = common_utils_instance. \
                                retry_call(remove_service_cmd, service_from_discovery_service_delete_try)
                        common_utils_instance.check_current_state_call(current_exit_code,
                                                                       'Service from Service Discovery',
                                                                       services[index]["service_id"])

    @staticmethod
    def _delete_namespace_service(environment, namespace_id):
        logging.info("Deleting namespace for cluster {}".format(environment))
        subprocess.call(
            ['aws', 'servicediscovery', 'delete-namespace', '--id', namespace_id, '--region', 'us-east-1'],
            stdout=FNULL)

    def delete_servicediscovery(self, environment):
        logging.info("Checking if there are AWS resources related to the service discovery of the {}"
                     " cluster".format(environment))
        cluster_information = self._check_if_ecs_cluster_exists(environment)
        if cluster_information['exists'] and not cluster_information['inactive']:
            logging.info("There is an ECS cluster with the name {} with {} services active {} tasks running".format(
                environment, cluster_information['ecs_cluster_information']['activeServicesCount'],
                cluster_information['ecs_cluster_information']['runningTasksCount']))
            self._stop_task_and_delete_services(environment)
        namespace_name = environment + '.local'
        logging.info("Checking if there is a namespace for service discovery of environment {}".format(environment))
        servicediscovery_namespaces_list_call = subprocess.Popen(
            ['aws', 'servicediscovery', 'list-namespaces', '--region', 'us-east-1'], stdout=subprocess.PIPE)
        actual_namespaces = json.loads(servicediscovery_namespaces_list_call.stdout.read())
        if self._check_servicediscovery_namespace_exists(actual_namespaces, namespace_name):
            logging.info("Exists namespace for service discovery of environment {}".format(environment))
            namespace_id = self._get_servicediscovery_id(actual_namespaces, namespace_name)
            services = self._get_services_in_namespace(environment, namespace_id)
            self._delete_services_in_namespace(environment, services)
            self._delete_namespace_service(environment, namespace_id)
        else:
            logging.error("Doesn't exists namespace for servicediscovery of environment {}".format(environment))

    def delete_ecs_cluster(self, environment):
        self.delete_servicediscovery(environment)
        logging.info("Checking if there is an ECS cluster for the environment {}".format(environment))
        cluster_information = self._check_if_ecs_cluster_exists(environment)
        if cluster_information['exists'] and not cluster_information['inactive']:
            logging.info("There is an ECS cluster for the environment {} with {} services active {} tasks running".
                         format(environment, cluster_information['ecs_cluster_information']['activeServicesCount'],
                                cluster_information['ecs_cluster_information']['runningTasksCount']))
            logging.info("ECS cluster for the environment {} is going to be removed".format(environment))
            cmd_call_remove_ecs_cluster = 'aws, ecs, delete-cluster, --cluster, ' + environment + ', --region' + \
                                          ', us-east-1'
            remove_ecs_cluster_call = subprocess.call(cmd_call_remove_ecs_cluster.split(', '), stdout=FNULL,
                                                      stderr=FNULL)
            common_utils_instance = common_utils_module.CommonUtils()
            common_utils_instance.check_current_state_call(remove_ecs_cluster_call,
                                                           'ECS Cluster', environment)
            if remove_ecs_cluster_call != 0:
                ecs_cluster_delete_try = 0
                current_exit_code = remove_ecs_cluster_call
                while common_utils_instance.can_retry_call(ecs_cluster_delete_try) and \
                        current_exit_code != 0:
                    current_exit_code, ecs_cluster_delete_try = common_utils_instance.retry_call(
                        cmd_call_remove_ecs_cluster, ecs_cluster_delete_try)
                common_utils_instance.check_current_state_call(current_exit_code, 'Security Group',
                                                               environment)
        elif cluster_information['exists'] and cluster_information['inactive']:
            logging.info("There is an ECS cluster for the environment {} but it's not going to be deleted because "
                         "it's INACTIVE and without pending tasks or services ".format(environment))
        else:
            logging.error("There isn't an ECS cluster for the environment {}".format(environment))

    def _check_if_ecs_cluster_exists(self, environment):
        cluster_exists = {'exists': False}
        cluster_exists_check_call = subprocess.Popen(['aws', 'ecs', 'describe-clusters', '--cluster', environment],
                                                     stdout=subprocess.PIPE, stderr=FNULL)
        cluster_exists_check_result_list = json.loads(cluster_exists_check_call.stdout.read())
        cluster_exists_check_result = cluster_exists_check_result_list['clusters']
        if len(cluster_exists_check_result) > 0:
            if self._check_ecs_cluster_is_active(cluster_exists_check_result[0]):
                cluster_exists.update({'exists': True,
                                       'inactive': False,
                                       'ecs_cluster_information': cluster_exists_check_result[0]})
            else:
                cluster_exists.update({'exists': True,
                                       'inactive': True})
        return cluster_exists

    @staticmethod
    def _check_ecs_cluster_is_active(cluster_info):
        ecs_cluster_is_active = False
        if cluster_info['status'] == "ACTIVE" or (
                cluster_info['status'] != "ACTIVE" and (cluster_info['registeredContainerInstancesCount'] > 0 or
                                                        cluster_info['runningTasksCount'] > 0 or cluster_info[
                                                            'pendingTasksCount'] > 0 or cluster_info[
                                                            'activeServicesCount']
                                                        > 0)):
            ecs_cluster_is_active = True
        return ecs_cluster_is_active

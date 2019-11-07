#!/bin/python


import os
import subprocess
import json
import logging

logging.basicConfig(level=logging.INFO)

FNULL = open(os.devnull, 'w')


class EcsServices:
    @staticmethod
    def _delete_ecs_service(cluster, service_name, service_id):
        logging.info(
            "Update desired count of service {} with id {} of cluster {} to 0 ".format(service_name, service_id,
                                                                                       cluster))
        subprocess.call(['aws', 'ecs', 'update-service', '--cluster', cluster, '--service', service_id,
                         '--desired-count', '0'], stdout=FNULL)
        logging.info("Deleting service {} with id {} of cluster {}".format(service_name, service_id, cluster))
        subprocess.call(['aws', 'ecs', 'delete-service', '--cluster', cluster, '--service', service_id],
                        stdout=FNULL)

    def _stop_task_and_delete_services(self, cluster):
        cmd_actual_task = "ecs-cli ps --cluster " + cluster + " --desired-status RUNNING --region us-east-1"
        try:
            actual_tasks = subprocess.check_output([cmd_actual_task], shell=True)
            if actual_tasks is not None:
                result = actual_tasks.decode().splitlines()[1:]
                for element in result:
                    task_identifier = element.split('/')[0]
                    service_name = element.split('/')[1].split(' ')[0]
                    service_id = cluster + '-' + service_name
                    self._delete_ecs_service(cluster, service_name, service_id)
                    logging.info("Stopping task {} of service {}".format(task_identifier, service_name))
                    subprocess.call(['aws', 'ecs', 'stop-task', '--cluster', cluster, '--task', task_identifier],
                                    stdout=FNULL)
        except subprocess.CalledProcessError as e:
            logging.info("Cluster {} doesn't have active running tasks".format(cluster))
        self._list_and_delete_all_services(cluster)

    def _list_and_delete_all_services(self, cluster):
        actual_services_call = subprocess.Popen(['aws', 'ecs', 'list-services', '--cluster', cluster, '--region',
                                                 'us-east-1'], stdout=subprocess.PIPE, stderr=FNULL)
        try:
            actual_services = json.loads(actual_services_call.stdout.read())
            if len(actual_services['serviceArns']) > 0:
                for element in actual_services['serviceArns']:
                    service_name = '-'.join(element.split('/')[1].split('-')[2:])
                    service_id = element.split('/')[1]
                    self._delete_ecs_service(cluster, service_name, service_id)
            else:
                logging.error("There are no services associated with the cluster {}".format(cluster))
        except ValueError as e:
            logging.error("There are no services associated with the cluster {}".format(cluster))

    @staticmethod
    def _check_servicediscovery_namespace_exists(actual_namespaces, cluster):
        if any(namespaces['Name'] == cluster for namespaces in actual_namespaces['Namespaces']):
            return True
        else:
            return False

    @staticmethod
    def _get_servicediscovery_id(actual_namespaces_json, namespace_name):
        for element in actual_namespaces_json['Namespaces']:
            if element['Name'] == namespace_name:
                return element['Id']

    @staticmethod
    def _get_services_in_namespace(cluster, namespace_id):
        services = []
        logging.info("Recovering services associated with namespace {}".format(namespace_id))
        servicediscovery_services_list_call = subprocess.Popen(
            ['aws', 'servicediscovery', 'list-services', '--region', 'us-east-1'], stdout=subprocess.PIPE)
        actual_services = json.loads(servicediscovery_services_list_call.stdout.read())
        for element in actual_services['Services']:
            if cluster in element['Name']:
                services.append({"service_name": element['Name'], "service_id": element['Id']})
        return services

    @staticmethod
    def _delete_services_in_namespace(cluster, services):
        if len(services) == 0:
            logging.info('There is no services to delete from cluster {}'.format(cluster))
        else:
            for index in range(len(services)):
                for key in services[index]:
                    logging.info(
                        "Deleting service with name {} and id {} from cluster {}".format(
                            services[index]["service_name"],
                            services[index]["service_id"],
                            cluster))
                subprocess.call(
                    ['aws', 'servicediscovery', 'delete-service', '--id', services[index]["service_id"], '--region',
                     'us-east-1'], stdout=FNULL)

    @staticmethod
    def _delete_namespace_service(cluster, namespace_id):
        logging.info("Deleting namespace for cluster {}".format(cluster))
        subprocess.call(
            ['aws', 'servicediscovery', 'delete-namespace', '--id', namespace_id, '--region', 'us-east-1'],
            stdout=FNULL)

    def delete_servicediscovery(self, cluster):
        logging.info("Servicediscovery for the cluster {} will be removed".format(cluster))
        self._stop_task_and_delete_services(cluster)
        namespace_name = cluster + '.local'
        servicediscovery_namespaces_list_call = subprocess.Popen(
            ['aws', 'servicediscovery', 'list-namespaces', '--region', 'us-east-1'], stdout=subprocess.PIPE)
        actual_namespaces = json.loads(servicediscovery_namespaces_list_call.stdout.read())
        if self._check_servicediscovery_namespace_exists(actual_namespaces, cluster):
            logging.info("Exists namespace for cluster {}".format(cluster))
            namespace_id = self._get_servicediscovery_id(actual_namespaces, namespace_name)
            services = self._get_services_in_namespace(cluster, namespace_id)
            self._delete_services_in_namespace(cluster, services)
            self._delete_namespace_service(cluster, namespace_id)
        else:
            logging.error("Doesn't exists namespace for cluster {}".format(cluster))

    def delete_ecs_cluster(self, cluster):
        self.delete_servicediscovery(cluster)
        logging.info("Cluster ECS {} it's going to be deleted".format(cluster))
        remove_ecs_cluster_call = subprocess.call(
                ['aws', 'ecs', 'delete-cluster', '--cluster', cluster, '--region', 'us-east-1'],
                stdout=FNULL, stderr=FNULL)
        if remove_ecs_cluster_call == 0:
            logging.info("Cluster ECS {} has been sucessfully removed".format(cluster))
        else:
            logging.error("Cluster ECS {} has not been deleted because it doesn't exist".format(cluster))


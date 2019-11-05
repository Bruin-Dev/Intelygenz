#!/bin/python


# !/usr/bin/python

import sys, getopt
import os
import subprocess
import json
import time
import logging

logging.basicConfig(level=logging.INFO)

FNULL = open(os.devnull, 'w')


def delete_ecs_service(cluster, service_name, service_id):
    logging.info(
        "Update desired count of service {} with id {} of cluster {} to 0 ".format(service_name, service_id,
                                                                                   cluster))
    subprocess.call(['aws', 'ecs', 'update-service', '--cluster', cluster, '--service', service_id,
                     '--desired-count', '0'], stdout=FNULL)
    logging.info("Deleting service {} with id {} of cluster {}".format(service_name, service_id, cluster))
    subprocess.call(['aws', 'ecs', 'delete-service', '--cluster', cluster, '--service', service_id],
                    stdout=FNULL)


def stop_task_and_delete_services(cluster):
    cmd_actual_task = "ecs-cli ps --cluster " + cluster + " --desired-status RUNNING --region us-east-1"
    try:
        actual_tasks = subprocess.check_output([cmd_actual_task], shell=True)
        if actual_tasks is not None:
            result = actual_tasks.decode().splitlines()[1:]
            for element in result:
                task_identifier = element.split('/')[0]
                service_name = element.split('/')[1].split(' ')[0]
                service_id = cluster + '-' + service_name
                delete_ecs_service(cluster, service_name, service_id)
                logging.info("Stopping task {} of service {}".format(task_identifier, service_name))
                subprocess.call(['aws', 'ecs', 'stop-task', '--cluster', cluster, '--task', task_identifier],
                                stdout=FNULL)
    except subprocess.CalledProcessError as e:
        logging.info("Cluster {} doesn't have active running tasks".format(cluster))
    list_and_delete_all_services(cluster)


def list_and_delete_all_services(cluster):
    actual_services_call = subprocess.Popen(['aws', 'ecs', 'list-services', '--cluster', cluster, '--region',
                                             'us-east-1'], stdout=subprocess.PIPE)
    actual_services = json.loads(actual_services_call.stdout.read())
    if len(actual_services['serviceArns']) > 0:
        for element in actual_services['serviceArns']:
            service_name = '-'.join(element.split('/')[1].split('-')[2:])
            service_id = element.split('/')[1]
            delete_ecs_service(cluster, service_name, service_id)
    else:
        logging.info("There isn't any services for the cluster {}".format(cluster))


def check_servicediscovery_namespace_exists(actual_namespaces, cluster):
    if any(namespaces['Name'] == cluster for namespaces in actual_namespaces['Namespaces']):
        return True
    else:
        return False


def get_servicediscovery_id(actual_namespaces_json, namespace_name):
    for element in actual_namespaces_json['Namespaces']:
        if element['Name'] == namespace_name:
            return element['Id']


def get_services_in_namespace(cluster, namespace_id):
    services = []
    logging.info("Recovering services associated with namespace {}".format(namespace_id))
    servicediscovery_services_list_call = subprocess.Popen(
        ['aws', 'servicediscovery', 'list-services', '--region', 'us-east-1'], stdout=subprocess.PIPE)
    actual_services = json.loads(servicediscovery_services_list_call.stdout.read())
    for element in actual_services['Services']:
        if cluster in element['Name']:
            services.append({"service_name": element['Name'], "service_id": element['Id']})
    return services


def delete_services_in_namespace(cluster, services):
    if len(services) == 0:
        logging.info('There is no services to delete from cluster {}'.format(cluster))
    else:
        for index in range(len(services)):
            for key in services[index]:
                logging.info(
                    "Deleting service with name {} and id {} from cluster {}".format(services[index]["service_name"],
                                                                                     services[index]["service_id"],
                                                                                     cluster))
            subprocess.call(
                ['aws', 'servicediscovery', 'delete-service', '--id', services[index]["service_id"], '--region',
                 'us-east-1'])


def delete_namespace_service(cluster, namespace_id):
    logging.info("Deleting namespace for cluster {}".format(cluster))
    subprocess.call(
        ['aws', 'servicediscovery', 'delete-namespace', '--id', namespace_id, '--region', 'us-east-1'], stdout=FNULL)


def delete_servicediscovery(cluster):
    logging.info("Servicediscovery for the cluster {} will be removed".format(cluster))
    stop_task_and_delete_services(cluster)
    namespace_name = cluster + '.local'
    servicediscovery_namespaces_list_call = subprocess.Popen(
        ['aws', 'servicediscovery', 'list-namespaces', '--region', 'us-east-1'], stdout=subprocess.PIPE)
    actual_namespaces = json.loads(servicediscovery_namespaces_list_call.stdout.read())
    if check_servicediscovery_namespace_exists(actual_namespaces, cluster):
        logging.info("Exists namespace for cluster {}".format(cluster))
        namespace_id = get_servicediscovery_id(actual_namespaces, namespace_name)
        services = get_services_in_namespace(cluster, namespace_id)
        delete_services_in_namespace(cluster, services)
        delete_namespace_service(cluster, namespace_id)
    else:
        logging.error("Doesn't exists namespace for cluster {}".format(cluster))


def delete_ecs_cluster(cluster):
    delete_servicediscovery(cluster)
    logging.info("Cluster {} it's going to be deleted".format(cluster))
    subprocess.call(
        ['aws', 'ecs', 'delete-cluster', '--cluster', cluster, '--region', 'us-east-1'], stdout=FNULL)


def check_redis_cluster_exists(cluster):
    redis_cluster_exists = {}
    try:
        redis_cluster_call = subprocess.Popen(
            ['aws', 'elasticache', 'describe-cache-clusters', '--cache-cluster-id', cluster, '--region', 'us-east-1'],
            stdout=subprocess.PIPE, stderr=FNULL)
        redis_cluster = json.loads(redis_cluster_call.stdout.read())
        if redis_cluster is not None:
            redis_cluster_exists.update({'exists': True, 'redis_cluster_information': redis_cluster})
    except ValueError as e:
        redis_cluster_exists.update({'exists': False})
    return redis_cluster_exists


def check_redis_cluster_is_deleted(cluster, start_time):
    timeout = start_time + 60 * 5
    correct_exit = False
    actual_time = time.time()
    while timeout > actual_time:
        redis_cluster_status = check_redis_cluster_exists(cluster)
        if redis_cluster_status['exists']:
            logging.info("Waiting for Redis cluster {} to be deleted".format(cluster))
            logging.info("Time elapsed for delete Redis cluster {} seconds".format(actual_time-start_time))
            logging.info("Actual state of Redis cluster is: {}".format(
                redis_cluster_status['redis_cluster_information']['CacheClusters'][0]['CacheClusterStatus']))
            time.sleep(30)
            actual_time = time.time()
        else:
            logging.info("Redis cluster {} has been deleted successfully".format(cluster))
            correct_exit = True
            break
    if timeout > actual_time and not correct_exit:
        logging.error("The maximum waiting time for deleting the Redis cluster "
                      "{} (5 minutes) has elapsed and it has not been possible to delete it".format(cluster))


def delete_redis_cluster(cluster):
    redis_cluster = check_redis_cluster_exists(cluster)
    if redis_cluster['exists']:
        logging.info("Redis cluster {} exists and has {} cache nodes".format(cluster,
                                                                             redis_cluster['redis_cluster_information']
                                                                             ['CacheClusters'][0]['NumCacheNodes']))
        logging.info("Redis cluster {} it's going to be deleted".format(cluster))
        subprocess.call(
            ['aws', 'elasticache', 'delete-cache-cluster', '--cache-cluster-id', cluster, '--region', 'us-east-1'],
            stdout=FNULL)
        start_time = time.time()
        check_redis_cluster_is_deleted(cluster, start_time)
    else:
        logging.error("Redis cluster {} doesn't exists".format(cluster))


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hc:s:e:r:", ["cluster=", "servicediscovery", "ecs-cluster", "redis-cluster"])
    except getopt.GetoptError:
        print('delete_deployments_resources.py -c <ecs_cluster_identifier> [-e] [-s] [-r]')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('delete_deployments_resources.py -c <ecs_cluster_identifier> [-e] [-s] [-r]')
            sys.exit()
        elif opt in ("-c", "--cluster"):
            cluster = arg
        elif opt in ("-s", "--servicediscovery"):
            delete_servicediscovery(cluster)
        elif opt in ("-e", "--ecs-cluster"):
            delete_ecs_cluster(cluster)
        elif opt in ("-r", "--redis-cluster"):
            delete_redis_cluster(cluster)


if __name__ == "__main__":
    main(sys.argv[1:])

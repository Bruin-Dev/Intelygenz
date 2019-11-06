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
                 'us-east-1'], stdout=FNULL)


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
            logging.info("Time elapsed for delete Redis cluster {} seconds".format(actual_time - start_time))
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


def check_alb_exists(cluster):
    alb_exists = {'exists': False}
    alb_list_call = subprocess.Popen(
        ['aws', 'elbv2', 'describe-load-balancers', '--region', 'us-east-1'],
        stdout=subprocess.PIPE, stderr=FNULL)
    alb_list = json.loads(alb_list_call.stdout.read())
    albs = alb_list['LoadBalancers']
    if len(albs) > 0:
        for element in albs:
            if element['LoadBalancerName'] == cluster and element['Type'] == 'application':
                alb_exists.update({'exists': True, 'alb_information': element})
    return alb_exists


def get_targets_groups_for_alb_and_cluster(alb_arn, cluster):
    target_groups = []
    target_group_list_call = subprocess.Popen(
        ['aws', 'elbv2', 'describe-target-groups', '--region', 'us-east-1'],
        stdout=subprocess.PIPE, stderr=FNULL)
    target_group_list = json.loads(target_group_list_call.stdout.read())['TargetGroups']
    if len(target_group_list) > 0:
        for element in target_group_list:
            if element['LoadBalancerArns']:
                for targetgroup_alb_arn in element['LoadBalancerArns']:
                    if alb_arn == targetgroup_alb_arn:
                        target_groups.append(element)
            elif cluster in element['TargetGroupName']:
                target_groups.append(element)
    return target_groups


def delete_targets_group_for_alb(alb_arn, cluster):
    target_groups_to_delete = get_targets_groups_for_alb_and_cluster(alb_arn, cluster)
    if len(target_groups_to_delete) > 0:
        for i in range(len(target_groups_to_delete)):
            target_group_arn = target_groups_to_delete[i]['TargetGroupArn']
            target_group_name = target_groups_to_delete[i]['TargetGroupName']
            logging.info("Deleting target group with name {} and arn {}".format(target_group_arn, target_group_name))
            subprocess.call(['aws', 'elbv2', 'delete-target-group', '--target-group-arn', target_group_arn],
                            stdout=FNULL)


def delete_alb(cluster):
    alb_exists = check_alb_exists(cluster)
    if alb_exists['exists']:
        logging.info("ALB with name {} exists".format(cluster))
        alb_arn = alb_exists['alb_information']['LoadBalancerArn']
        logging.info("ALB cluster ARN is: {}".format(alb_arn))
        logging.info("Deleting alb with name {} and arn {}".format(cluster, alb_arn))
        subprocess.call(['aws', 'elbv2', 'delete-load-balancer', '--load-balancer-arn', alb_arn], stdout=FNULL)
        delete_targets_group_for_alb(alb_arn, cluster)
    else:
        logging.error("ALB with name {} doesn't exists".format(cluster))


def get_security_groups(cluster):
    security_groups = []
    security_groups_list_call = subprocess.Popen(['aws', 'ec2', 'describe-security-groups', '--filters',
                                                  'Name=tag:Environment, Values=' + cluster, '--region', 'us-east-1'],
                                                 stdout=subprocess.PIPE, stderr=FNULL)
    security_groups_list = json.loads(security_groups_list_call.stdout.read())['SecurityGroups']
    if len(security_groups_list) > 0:
        for element in security_groups_list:
            security_groups.append(element)
    return security_groups


def delete_security_groups(cluster):
    security_groups_cluster = get_security_groups(cluster)
    security_groups_cluster_size = len(security_groups_cluster)
    if security_groups_cluster_size > 0:
        logging.info(
            "There are {} security group/s associated with cluster {}".format(security_groups_cluster_size, cluster))
        for element in security_groups_cluster:
            security_group_name = element['GroupName']
            security_group_id = element['GroupId']
            logging.info("Deleting SecurityGroup with name {} and id {}".format(security_group_name, security_group_id))
            subprocess.call(['aws', 'ec2', 'delete-security-group', '--group-id', security_group_id], stdout=FNULL)
    else:
        logging.error("There isn't any security group associated with cluster {}".format(cluster))


def get_cluster_dashboard(cluster):
    cluster_dashboard_exists = {'exists': False}
    cluster_dashboard_list_call = subprocess.Popen(['aws', 'cloudwatch', 'list-dashboards'], stdout=subprocess.PIPE,
                                                   stderr=FNULL)
    cluster_dashboard_list = json.loads(cluster_dashboard_list_call.stdout.read())['DashboardEntries']
    if len(cluster_dashboard_list) > 0:
        cluster_dashboard_name = 'cluster-' + cluster
        for element in cluster_dashboard_list:
            if element['DashboardName'] == cluster_dashboard_name:
                cluster_dashboard_exists.update({'exists': True, 'dashboard_information': element})
    return cluster_dashboard_exists


def delete_dashboard(cluster):
    cluster_dashboard = get_cluster_dashboard(cluster)
    if cluster_dashboard['exists']:
        dashboard_name = cluster_dashboard['dashboard_information']['DashboardName']
        logging.info("Dashboard for cluster {} exists".format(cluster))
        logging.info("Dashboard with name {} it's going to be removed".format(dashboard_name))
        subprocess.call(['aws', 'cloudwatch', 'delete-dashboards', '--dashboard-names', dashboard_name], stdout=FNULL)
    else:
        logging.error("Dashboard for cluster {} doesn't exists".format(cluster))


def get_cluster_alarms(cluster):
    cluster_alarms = {'has_alarms': False}
    cluster_alarms_list_call = subprocess.Popen(['aws', 'cloudwatch', 'describe-alarms', '--region', 'us-east-1'],
                                                stdout=subprocess.PIPE, stderr=FNULL)
    cluster_alarms_list = json.loads(cluster_alarms_list_call.stdout.read())['MetricAlarms']
    if len(cluster_alarms_list) > 0:
        cluster_alarm_elements = {}
        for i in range(len(cluster_alarms_list)):
            alarm_name = cluster_alarms_list[i]['AlarmName']
            if cluster in alarm_name:
                cluster_alarm_elements.update({i: alarm_name})
        if len(cluster_alarm_elements) > 0:
            cluster_alarms.update({'has_alarms': True, 'cluster_alarms': cluster_alarm_elements})
    return cluster_alarms


def delete_alarms(cluster):
    cluster_alarms = get_cluster_alarms(cluster)
    if cluster_alarms['has_alarms']:
        logging.info("There are alarms associated with cluster: {}".format(cluster))
        for i in cluster_alarms['cluster_alarms'].keys():
            alarm_name = cluster_alarms['cluster_alarms'][i]
            logging.info("Alarm with name {} it's going to be deleted".format(alarm_name))
            subprocess.call(['aws', 'cloudwatch', 'delete-alarms', '--alarm-names', alarm_name], stdout=FNULL)
    else:
        logging.error("There aren't alarms associated with cluster: {}".format(cluster))


def get_log_metric_for_cluster(cluster):
    metrics_logs_for_cluster = {'has_log_metrics': False}
    metrics_logs_list_call = subprocess.Popen(
        ['aws', 'logs', 'describe-metric-filters', '--log-group-name', cluster, '--region',
         'us-east-1'], stdout=subprocess.PIPE, stderr=FNULL)
    try:
        metrics_logs_list = json.loads(metrics_logs_list_call.stdout.read())['metricFilters']
        if metrics_logs_list is not None and len(metrics_logs_list) > 0:
            metrics_logs_for_cluster_elements = {}
            for i in range(len(metrics_logs_list)):
                metric_log_filter = metrics_logs_list[i]['filterName']
                metrics_logs_for_cluster_elements.update({i: metric_log_filter})
                logging.debug("Cluster has associated metric with filterName {}".format(metric_log_filter))
            metrics_logs_for_cluster.update({'has_log_metrics': True, 'log_metrics_filters':
                                            metrics_logs_for_cluster_elements})
    except ValueError as e:
        pass
    return metrics_logs_for_cluster


def delete_log_metrics(cluster):
    log_metrics_for_cluster = get_log_metric_for_cluster(cluster)
    if log_metrics_for_cluster['has_log_metrics']:
        logging.info("Cluster {} has associated {} log metric/s filter/s".format(cluster,
                                                                                 len(log_metrics_for_cluster['log_metrics_filters'])))
        for i in log_metrics_for_cluster['log_metrics_filters'].keys():
            log_metric_filter_name = log_metrics_for_cluster['log_metrics_filters'][i]
            logging.info("Log metric filter with name {} it's going to be deleted".format(log_metric_filter_name))
            subprocess.call(['aws', 'logs', 'delete-metric-filter', '--log-group-name', cluster, '--filter-name',
                             log_metric_filter_name], stdout=FNULL)
    else:
        logging.error("Cluster {} doesn't have any log metric associated to its log group".format(cluster))


def check_log_group_exists(cluster):
    log_group_list_call = subprocess.Popen(
        ['aws', 'logs', 'describe-log-groups', '--region', 'us-east-1'], stdout=subprocess.PIPE, stderr=FNULL)
    log_group_list = json.loads(log_group_list_call.stdout.read())['logGroups']
    if len(log_group_list) > 0:
        if any(log_group['logGroupName'] == cluster for log_group in log_group_list):
            return True
    return False


def delete_log_group(cluster):
    if check_log_group_exists(cluster):
        logging.info("Cluster {} has a log group associated".format(cluster))
        logging.info("Log group with name {} it's going to be deleted".format(cluster))
        subprocess.call(['aws', 'logs', 'delete-log-group', '--log-group-name', cluster], stdout=FNULL)
    else:
        logging.error("Cluster {} doesn't have any log group associated".format(cluster))


def delete_metrics_resources(cluster):
    delete_dashboard(cluster)
    delete_alarms(cluster)
    delete_log_metrics(cluster)
    delete_log_group(cluster)


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hc:d:e:r:a:s:m:",
                                   ["cluster=", "servicediscovery", "ecs-cluster", "redis-cluster", "alb",
                                    "security-groups", "metrics"])
    except getopt.GetoptError:
        print('delete_deployments_resources.py -c <ecs_cluster_identifier> [-e] [-d] [-r] [-a] [-s] [-m]')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('delete_deployments_resources.py -c <ecs_cluster_identifier> [-e] [-d] [-r] [-a] [-s] [-m]')
            sys.exit()
        elif opt in ("-c", "--cluster"):
            cluster = arg
        elif opt in ("-d", "--service-discovery"):
            delete_servicediscovery(cluster)
        elif opt in ("-e", "--ecs-cluster"):
            delete_ecs_cluster(cluster)
        elif opt in ("-r", "--redis-cluster"):
            delete_redis_cluster(cluster)
        elif opt in ("-a", "--alb"):
            delete_alb(cluster)
        elif opt in ("-s", "--security-groups"):
            delete_security_groups(cluster)
        elif opt in ("-m", "--metrics"):
            delete_metrics_resources(cluster)


if __name__ == "__main__":
    main(sys.argv[1:])

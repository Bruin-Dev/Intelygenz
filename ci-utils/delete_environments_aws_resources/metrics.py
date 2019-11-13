#!/bin/python


import os
import subprocess
import json
import logging

logging.basicConfig(level=logging.INFO)

FNULL = open(os.devnull, 'w')


class Metrics:
    @staticmethod
    def _get_cluster_dashboard(environment):
        cluster_dashboard_exists = {'exists': False}
        cluster_dashboard_list_call = subprocess.Popen(['aws', 'cloudwatch', 'list-dashboards'], stdout=subprocess.PIPE,
                                                       stderr=FNULL)
        cluster_dashboard_list = json.loads(cluster_dashboard_list_call.stdout.read())['DashboardEntries']
        if len(cluster_dashboard_list) > 0:
            cluster_dashboard_name = 'cluster-' + environment
            for element in cluster_dashboard_list:
                if element['DashboardName'] == cluster_dashboard_name:
                    cluster_dashboard_exists.update({'exists': True, 'dashboard_information': element})
        return cluster_dashboard_exists

    def _delete_dashboard(self, environment):
        cluster_dashboard = self._get_cluster_dashboard(environment)
        if cluster_dashboard['exists']:
            dashboard_name = cluster_dashboard['dashboard_information']['DashboardName']
            logging.info("There is a dashboard for environment {}".format(environment))
            logging.info("Dashboard with name {} it's going to be removed".format(dashboard_name))
            subprocess.call(['aws', 'cloudwatch', 'delete-dashboards', '--dashboard-names', dashboard_name],
                            stdout=FNULL)
        else:
            logging.error("There isn't any dashboard for environment {}".format(environment))

    @staticmethod
    def _get_cluster_alarms(environment):
        cluster_alarms = {'has_alarms': False}
        cluster_alarms_list_call = subprocess.Popen(['aws', 'cloudwatch', 'describe-alarms', '--region', 'us-east-1'],
                                                    stdout=subprocess.PIPE, stderr=FNULL)
        cluster_alarms_list = json.loads(cluster_alarms_list_call.stdout.read())['MetricAlarms']
        if len(cluster_alarms_list) > 0:
            cluster_alarm_elements = {}
            for i in range(len(cluster_alarms_list)):
                alarm_name = cluster_alarms_list[i]['AlarmName']
                if environment in alarm_name:
                    cluster_alarm_elements.update({i: alarm_name})
            if len(cluster_alarm_elements) > 0:
                cluster_alarms.update({'has_alarms': True, 'cluster_alarms': cluster_alarm_elements})
        return cluster_alarms

    def _delete_alarms(self, environment):
        cluster_alarms = self._get_cluster_alarms(environment)
        if cluster_alarms['has_alarms']:
            logging.info("There are alarms associated with the environment: {}".format(environment))
            for i in cluster_alarms['cluster_alarms'].keys():
                alarm_name = cluster_alarms['cluster_alarms'][i]
                logging.info("Alarm with name {} it's going to be deleted".format(alarm_name))
                subprocess.call(['aws', 'cloudwatch', 'delete-alarms', '--alarm-names', alarm_name], stdout=FNULL)
        else:
            logging.error("There aren't alarms associated with the environment: {}".format(environment))

    @staticmethod
    def _get_log_metric_for_cluster(environment):
        metrics_logs_for_cluster = {'has_log_metrics': False}
        metrics_logs_list_call = subprocess.Popen(
            ['aws', 'logs', 'describe-metric-filters', '--log-group-name', environment, '--region',
             'us-east-1'], stdout=subprocess.PIPE, stderr=FNULL)
        try:
            metrics_logs_list = json.loads(metrics_logs_list_call.stdout.read())['metricFilters']
            if metrics_logs_list is not None and len(metrics_logs_list) > 0:
                metrics_logs_for_cluster_elements = {}
                for i in range(len(metrics_logs_list)):
                    metric_log_filter = metrics_logs_list[i]['filterName']
                    metrics_logs_for_cluster_elements.update({i: metric_log_filter})
                    logging.debug("The environment has associated metric with filterName {}".format(metric_log_filter))
                metrics_logs_for_cluster.update({'has_log_metrics': True, 'log_metrics_filters':
                                                metrics_logs_for_cluster_elements})
        except ValueError as e:
            pass
        return metrics_logs_for_cluster

    @staticmethod
    def _delete_log_metrics(environment, log_metrics_for_cluster):
        for i in log_metrics_for_cluster.keys():
            log_metric_filter_name = log_metrics_for_cluster[i]
            logging.info("Log metric filter with name {} it's going to be deleted".format(log_metric_filter_name))
            subprocess.call(
                ['aws', 'logs', 'delete-metric-filter', '--log-group-name', environment, '--filter-name',
                 log_metric_filter_name], stdout=FNULL)

    @staticmethod
    def _check_log_group_exists(cluster):
        log_group_list_call = subprocess.Popen(
            ['aws', 'logs', 'describe-log-groups', '--region', 'us-east-1'], stdout=subprocess.PIPE, stderr=FNULL)
        log_group_list = json.loads(log_group_list_call.stdout.read())['logGroups']
        if len(log_group_list) > 0:
            if any(log_group['logGroupName'] == cluster for log_group in log_group_list):
                return True
        return False

    def _delete_log_group(self, environment):
        if self._check_log_group_exists(environment):
            log_metrics_for_cluster = self._get_log_metric_for_cluster(environment)
            if log_metrics_for_cluster['has_log_metrics']:
                logging.info("The environment {} has associated {} log metric/s filter/s".format(environment, len(
                    log_metrics_for_cluster['log_metrics_filters'])))
                self._delete_log_metrics(environment, log_metrics_for_cluster['log_metrics_filters'])
            else:
                logging.error("The environment {} doesn't have any log metric associated to its log group".
                              format(environment))
            logging.info("The environment {} has a log group associated".format(environment))
            logging.info("Log group with name {} it's going to be deleted".format(environment))
            subprocess.call(['aws', 'logs', 'delete-log-group', '--log-group-name', environment], stdout=FNULL)
        else:
            logging.error("The environment {} doesn't have any log group associated".format(environment))

    def delete_metrics_resources(self, environment):
        logging.info("Checking if there are metrics resources for environment {}".format(environment))
        self._delete_dashboard(environment)
        self._delete_alarms(environment)
        self._delete_log_group(environment)

#!/bin/python


import os
import subprocess
import json
import logging

logging.basicConfig(level=logging.INFO)

FNULL = open(os.devnull, 'w')


class ApplicationLoadBalancer:
    @staticmethod
    def _check_alb_exists(cluster):
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

    @staticmethod
    def _get_targets_groups_for_alb_and_cluster(alb_arn, cluster):
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

    def _delete_targets_group_for_alb(self, alb_arn, cluster):
        target_groups_to_delete = self._get_targets_groups_for_alb_and_cluster(alb_arn, cluster)
        if len(target_groups_to_delete) > 0:
            for i in range(len(target_groups_to_delete)):
                target_group_arn = target_groups_to_delete[i]['TargetGroupArn']
                target_group_name = target_groups_to_delete[i]['TargetGroupName']
                logging.info("Deleting target group with name {} and arn {}".format(target_group_arn, target_group_name))
                subprocess.call(['aws', 'elbv2', 'delete-target-group', '--target-group-arn', target_group_arn],
                                stdout=FNULL)

    def delete_alb(self, cluster):
        alb_exists = self._check_alb_exists(cluster)
        if alb_exists['exists']:
            logging.info("ALB with name {} exists".format(cluster))
            alb_arn = alb_exists['alb_information']['LoadBalancerArn']
            logging.info("ALB cluster ARN is: {}".format(alb_arn))
            logging.info("Deleting alb with name {} and arn {}".format(cluster, alb_arn))
            subprocess.call(['aws', 'elbv2', 'delete-load-balancer', '--load-balancer-arn', alb_arn], stdout=FNULL)
            self._delete_targets_group_for_alb(alb_arn, cluster)
        else:
            logging.error("ALB with name {} doesn't exists".format(cluster))
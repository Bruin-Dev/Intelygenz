#!/bin/python


import os
import subprocess
import json
import logging

logging.basicConfig(level=logging.INFO)

FNULL = open(os.devnull, 'w')


class SecurityGroups:
    @staticmethod
    def _get_security_groups(cluster):
        security_groups = []
        security_groups_list_call = subprocess.Popen(['aws', 'ec2', 'describe-security-groups', '--filters',
                                                      'Name=tag:Environment, Values=' + cluster, '--region', 'us-east-1'],
                                                     stdout=subprocess.PIPE, stderr=FNULL)
        security_groups_list = json.loads(security_groups_list_call.stdout.read())['SecurityGroups']
        if len(security_groups_list) > 0:
            for element in security_groups_list:
                security_groups.append(element)
        return security_groups

    def delete_security_groups(self, cluster):
        logging.info("Checking if there are security groups associated with the environment {}".format(cluster))
        security_groups_cluster = self._get_security_groups(cluster)
        security_groups_cluster_size = len(security_groups_cluster)
        if security_groups_cluster_size > 0:
            logging.info(
                "There are {} security group/s associated with cluster {}".format(security_groups_cluster_size, cluster))
            for element in security_groups_cluster:
                security_group_name = element['GroupName']
                security_group_id = element['GroupId']
                logging.info("Deleting SecurityGroup with name {} and id {}".format(security_group_name,
                                                                                    security_group_id))
                subprocess.call(['aws', 'ec2', 'delete-security-group', '--group-id', security_group_id], stdout=FNULL)
        else:
            logging.error("There isn't any security group associated with cluster {}".format(cluster))
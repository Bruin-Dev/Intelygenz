#!/bin/python


import os
import subprocess
import json
import logging

import common_utils as common_utils_module

logging.basicConfig(level=logging.INFO)

FNULL = open(os.devnull, 'w')


class SecurityGroups:
    @staticmethod
    def _get_security_groups(cluster):
        security_groups = []
        security_groups_list_call = subprocess.Popen(['aws', 'ec2', 'describe-security-groups', '--filters',
                                                      'Name=tag:Environment, Values=' + cluster, '--region',
                                                      'us-east-1'],
                                                     stdout=subprocess.PIPE, stderr=FNULL)
        security_groups_list = json.loads(security_groups_list_call.stdout.read())['SecurityGroups']
        if len(security_groups_list) > 0:
            for element in security_groups_list:
                security_groups.append(element)
        return security_groups

    def delete_security_groups(self, environment):
        logging.info("Checking if there are security groups associated with the environment {}".format(environment))
        security_groups_cluster = self._get_security_groups(environment)
        security_groups_cluster_size = len(security_groups_cluster)
        if security_groups_cluster_size > 0:
            common_utils_instance = common_utils_module.CommonUtils()
            logging.info(
                "There are {} security group/s associated with the environment {}".format(
                    security_groups_cluster_size, environment))
            for element in security_groups_cluster:
                security_group_name = element['GroupName']
                security_group_id = element['GroupId']
                logging.info("Deleting Security Group with name {} and id {}".format(security_group_name,
                                                                                     security_group_id))
                cmd_call_remove_sg = 'aws, ec2, delete-security-group, --group-id, ' + security_group_id
                remove_security_group = subprocess.call(cmd_call_remove_sg.split(', '), stdout=FNULL)
                common_utils_instance.check_current_state_call(remove_security_group,
                                                               'Security Group', security_group_name)
                if remove_security_group != 0:
                    logging.info("SecurityGroup delete enter in remove_security distinct 0")
                    security_group_delete_try = 0
                    current_exit_code = remove_security_group
                    logging.info("security_group_delete_try is {}".format(security_group_delete_try))
                    logging.info("remove_security_group is {}".format(remove_security_group))
                    while common_utils_instance.can_retry_call(security_group_delete_try) and \
                            current_exit_code != 0:
                        logging.info("security_group_delete_try is {}".format(security_group_delete_try))
                        logging.info("current_exit_code is {}".format(current_exit_code))
                        current_exit_code, security_group_delete_try = common_utils_instance.retry_call(
                            cmd_call_remove_sg, security_group_delete_try)
                    common_utils_instance.check_current_state_call(current_exit_code, 'Security Group',
                                                                   security_group_name)
        else:
            logging.error("There isn't any security group associated with the environment {}".format(environment))

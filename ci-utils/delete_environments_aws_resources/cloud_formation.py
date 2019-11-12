#!/bin/python


import os
import subprocess
import json
import time
import logging

import common_utils as common_utils_module

logging.basicConfig(level=logging.INFO)

FNULL = open('/dev/null', 'w')


class CloudFormation:
    _cloud_formation_environment_prefix = 'SnsTopicMetTelAutomationAlarms-'

    def delete_cloud_formation_resources(self, environment):
        cloud_formation_for_environment = self._check_cloud_formation_for_environment(environment)
        logging.info("Checking if there is a CloudFormation resource for environment {}".format(environment))
        cloud_formation_environment_exists = cloud_formation_for_environment['exists']
        cloud_formation_delete = self._check_delete_result(cloud_formation_environment_exists, environment)
        logging.info("cloud_formation_delete result is {}".format(cloud_formation_delete))
        return cloud_formation_delete

    def _check_delete_result(self, cloud_formation_environment_exists, environment):
        cloud_formation_delete_result = {}
        if cloud_formation_environment_exists:
            common_utils_instance = common_utils_module.CommonUtils()
            stack_name = self._cloud_formation_environment_prefix + environment
            logging.info("There is a CloudFormation resource for environment {} with name {}"
                         .format(environment, stack_name))
            logging.info("CloudFormation resource for environment {} it's going to be deleted".format(environment))
            cmd_call_remove_cloudformation_stack = 'aws, cloudformation, delete-stack, --stack-name, ' \
                                                   + stack_name + ', --region' + ', us-east-1'
            remove_cloudformation_stack = subprocess.call(cmd_call_remove_cloudformation_stack.split(', '))
            common_utils_instance.check_current_state_call(remove_cloudformation_stack,
                                                           'CloudFormation stack', stack_name)
            if remove_cloudformation_stack == 0:
                cloud_formation_delete_result.update({'exists': cloud_formation_environment_exists,
                                                      'success_delete': True})
            else:
                cloud_formation_delete_result.update({'exists': cloud_formation_environment_exists,
                                                      'success_delete': False})
        else:
            logging.error("There isn't a CloudFormation resource for environment {}".format(environment))
            cloud_formation_delete_result.update({'exists': cloud_formation_environment_exists})
        return cloud_formation_delete_result

    # def _delete_cloud_formation_resources(self, arn_id):
    #     common_utils_instance = common_utils_module.CommonUtils()
    #     logging.info("AWS topic with arn {} it's going to be deleted".format(arn_id))
    #     cmd_call_remove_sns_topic = 'aws, sns, delete-topic, --topic-arn, ' + arn_id
    #     remove_sns_topic = subprocess.call(cmd_call_remove_sns_topic.split(', '))
    #     common_utils_instance.check_current_state_call(remove_cloudformation_stack,
    #                                                    'Sns topic', stack_name)

    def _check_cloud_formation_for_environment(self, environment):
        cloud_formation = {'exists': False}
        cloud_formation_name = self._cloud_formation_environment_prefix + environment
        cloud_formation_list_call = subprocess.Popen(['aws', 'cloudformation', 'list-stack-resources',
                                                      '--stack-name', cloud_formation_name, '--region',
                                                      'us-east-1'],
                                                     stdout=subprocess.PIPE, stderr=FNULL)
        try:
            cloud_formation_list = json.loads(cloud_formation_list_call.stdout.read())['StackResourceSummaries']
            if len(cloud_formation_list) > 0:
                cloud_formation.update({'exists': True,
                                        'cloud_formation_information': cloud_formation_list[0]})
        except ValueError as e:
            pass
        return cloud_formation

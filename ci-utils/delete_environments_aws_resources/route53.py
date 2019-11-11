#!/bin/python


import os
import subprocess
import json
import logging

import common_utils as common_utils_module

logging.basicConfig(level=logging.INFO)

FNULL = open('/dev/null', 'w')


class Route53:
    _hosted_zone_for_records_name = 'mettel-automation.net.'

    def delete_environment_record_set(self, environment):
        hosted_zone_information = self._check_hosted_zone_for_records()
        if hosted_zone_information['exists']:
            hosted_zone_id = hosted_zone_information['hosted_zone_id']
            logging.info("hosted_zone_id is {}".format(hosted_zone_id))
            environment_record = self._check_resource_record_environment(hosted_zone_id, environment)
            if environment_record['exists']:
                logging.info("There is a record set for environment {} in hosted-zone with {}".
                             format(environment, hosted_zone_id))
                record_set_id_to_delete = environment_record['record_information']
                logging.info("Record set {} it's going to be deleted".format(record_set_id_to_delete))
                data_record_to_delete = {}
                data_record_to_delete_changes = [{'Action': 'DELETE',
                                                  'ResourceRecordSet': environment_record['record_information']}]
                data_record_to_delete['Changes'] = data_record_to_delete_changes
                data_record_to_delete['Comment'] = 'Removing record with name ' + \
                                                   environment_record['record_information']['Name']
                data_record_to_delete_json = json.dumps(data_record_to_delete)
                subprocess.call(['aws', 'route53', 'change-resource-record-sets', '--hosted-zone-id',
                                 hosted_zone_id, '--region', 'us-east-1',
                                 '--change-batch', data_record_to_delete_json])
            else:
                logging.error("There isn't a record set for environment {} in hosted-zone with {}".
                              format(environment, environment_record['hosted_zone_id']))

    def _check_hosted_zone_for_records(self):
        hosted_zone_of_hosted_zone_for_records = {'exists': False}
        hosted_zones_list_call = subprocess.Popen(['aws', 'route53', 'list-hosted-zones', '--region', 'us-east-1'],
                                                  stdout=subprocess.PIPE, stderr=FNULL)
        hosted_zones_groups_list = json.loads(hosted_zones_list_call.stdout.read())['HostedZones']
        if len(hosted_zones_groups_list) > 0:
            for element in hosted_zones_groups_list:
                if element['Name'] == self._hosted_zone_for_records_name:
                    hosted_zone_of_hosted_zone_for_records.update({'exists': True, 'hosted_zone_id': element['Id']})
                    break
        return hosted_zone_of_hosted_zone_for_records

    def _check_resource_record_environment(self, hosted_zone_id, environment):
        resource_record_environment = {'exists': False}
        resources_records_set_list_call = subprocess.Popen(['aws', 'route53', 'list-resource-record-sets',
                                                            '--hosted-zone-id', hosted_zone_id, '--region',
                                                            'us-east-1'], stdout=subprocess.PIPE, stderr=FNULL)
        resources_records_set_list = json.loads(resources_records_set_list_call.stdout.read())['ResourceRecordSets']
        if len(resources_records_set_list) > 0:
            record_set_to_search = environment.split('-')[1] + '.' + self._hosted_zone_for_records_name
            for element in resources_records_set_list:
                if element['Name'] == record_set_to_search:
                    resource_record_environment.update({'exists': True, 'record_information': element})
        return resource_record_environment

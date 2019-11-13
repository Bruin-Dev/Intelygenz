#!/bin/python


import os
import subprocess
import json
import logging
import sys
import yaml
import getopt

logging.basicConfig(level=logging.INFO)

FNULL = open(os.devnull, 'w')


def _print_usage():
    print('service_discovery.py -e <environment>')


class ServiceDiscovery:
    def generate_config_aws_nuke(self, environment):
        self._generate_resources_rules_aws_nuke_cloudwatch_logs_log_group(environment)
        self._generate_servicediscovery_resources_rules_aws_nuke(environment)

    def _generate_resources_rules_aws_nuke_cloudwatch_logs_log_group(self, environment):
        cloudwatch_logs_log_group_entry_regex_elements = [environment,
                                                          '/aws/ecs/containerinsights/'
                                                          + environment + '/performance']
        cloudwatch_logs_log_group_entry = self._create_dict_entry_aws_nuke_regex_list(cloudwatch_logs_log_group_entry_regex_elements)
        self._add_aws_entry_rule_to_config('CloudWatchLogsLogGroup', cloudwatch_logs_log_group_entry)

    def _generate_servicediscovery_resources_rules_aws_nuke(self, environment):
        logging.info("Checking if there is a namespace for service discovery of environment {}".format(environment))
        servicediscovery_namespaces_list_call = subprocess.Popen(
            ['aws', 'servicediscovery', 'list-namespaces', '--region', 'us-east-1'], stdout=subprocess.PIPE)
        actual_namespaces = json.loads(servicediscovery_namespaces_list_call.stdout.read())
        if self._check_servicediscovery_namespace_exists(actual_namespaces, environment):
            namespace_id = self._get_servicediscovery_id(actual_namespaces, environment)
            logging.info("Exists namespace for service discovery of environment {} with id {}".format(environment,
                                                                                                      namespace_id))
            namespace_aws_nuke_entry = self._create_dict_entry_aws_nuke_service_discovery_namespace(namespace_id)
            self._add_aws_entry_rule_to_config('ServiceDiscoveryNamespace', namespace_aws_nuke_entry)
            services = self._get_services_in_namespace(environment, namespace_id)
            if len(services) > 0:
                services_aws_nuke_entry = self._create_dict_entry_aws_nuke_service_discovery_services(services)
                self._add_aws_entry_rule_to_config('ServiceDiscoveryService', services_aws_nuke_entry)
        else:
            logging.error("Doesn't exists namespace for servicediscovery of environment {}".format(environment))

    @staticmethod
    def _check_servicediscovery_namespace_exists(actual_namespaces, environment):
        environment_namespace_name = environment + '.local'
        if any(namespaces['Name'] == environment_namespace_name for namespaces in actual_namespaces['Namespaces']):
            return True
        else:
            return False

    @staticmethod
    def _get_servicediscovery_id(actual_namespaces_json, environment):
        namespace_name = environment + '.local'
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
                services.append({"service_id": element['Id']})
        return services

    @staticmethod
    def _create_dict_entry_aws_nuke_value_invert(value):
        return [{'value': value, 'invert': True}]

    @staticmethod
    def _create_dict_entry_aws_nuke_service_discovery_namespace(servicediscovery_namespace_id):
        return [{'value': servicediscovery_namespace_id, 'invert': True}]

    @staticmethod
    def _create_dict_entry_aws_nuke_regex_list(elements):
        return [{'type': 'regex', 'value': '|'.join(elements), 'invert': True}]

    @staticmethod
    def _create_dict_entry_aws_nuke_service_discovery_services(services):
        dict_entry_list = ''
        for index in range(len(services)):
            for key in services[index]:
                if index == 0:
                    dict_entry_list = services[index]["service_id"]
                else:
                    dict_entry_list = dict_entry_list + '|' + services[index]["service_id"]
        return [{'type': 'regex', 'value': dict_entry_list, 'invert': True}]

    @staticmethod
    def _add_aws_entry_rule_to_config(key, dict_entry):
        with open(r'config.yml') as file:
            config_yaml_file = yaml.load(file, Loader=yaml.FullLoader)
        config_yaml_file['accounts']['374050862540']['filters'][key] = dict_entry
        logging.info("Change is {}".format(config_yaml_file['accounts']['374050862540']['filters'][key]))
        with open(r'config.yml', 'w') as file:
            yaml.dump(config_yaml_file, file)


if __name__ == "__main__":
    argv = sys.argv[1:]

    try:
        opts, args = getopt.getopt(argv, "he:",
                                   ["environment="])
    except getopt.GetoptError:
        _print_usage()
        sys.exit(2)

    if argv[0] != "-h" and (argv[0] != "-e"):
        _print_usage()
        sys.exit(2)

    _, environment = opts.pop(0)

    service_discovery_instance = ServiceDiscovery()
    ServiceDiscovery().generate_config_aws_nuke(environment)

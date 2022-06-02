#!/bin/python


import getopt
import json
import logging
import os
import subprocess
import sys

import yaml

logging.basicConfig(level=logging.INFO)

FNULL = open(os.devnull, "w")

_config_template = os.path.join(os.getcwd(), "ci-utils", "aws-nuke", "config_template.yml")
_config_file = os.path.join(os.getcwd(), "ci-utils", "aws-nuke", "config.yml")
_aws_service_discovery_resources_list = ["ServiceDiscoveryNamespace", "ServiceDiscoveryService"]
_aws_common_resources_list = [
    "CloudWatchLogsLogGroup",
    "CloudWatchAlarm",
    "CloudFormationStack" "ElasticacheCacheCluster",
    "ElasticacheSubnetGroup",
    "ElasticacheSubnetGroup" "ECSService",
    "ECSTaskDefinition" "ECSTaskDefinition",
    "ELBv2",
    "ELBv2TargetGroup",
    "EC2SecurityGroup",
]


def _print_usage():
    print("aws_nuke_conf_generator.py -e <environment_name>")


class AWSNukeConfigurationGenerator:
    def generate_config_aws_nuke(self, environment_name):
        aws_nuke_rules = []
        aws_nuke_specific_rules = self._generate_aws_nukes_rules_specific_rules(environment_name)
        aws_nuke_no_specific_rules = self._generate_aws_nuke_general_configuration_rules_environment(environment_name)
        if len(aws_nuke_specific_rules) > 0:
            aws_nuke_rules.extend(aws_nuke_specific_rules)
        aws_nuke_rules.extend(aws_nuke_no_specific_rules)
        self._add_aws_entries_rule_to_config(aws_nuke_rules)

    def _generate_aws_nukes_rules_specific_rules(self, environment_name):
        specific_rules_list = []
        aws_services_discovery_rules = self._generate_aws_nuke_configuration_for_service_discovery_environment(
            environment_name
        )
        aws_services_ecs_cluster_rules = self._generate_ecs_cluster_for_environment_rules(environment_name)
        if len(aws_services_discovery_rules) > 0:
            logging.info(
                f"Generated aws-nuke filters for {', '.join(_aws_service_discovery_resources_list)}" f" AWS resources"
            )
            specific_rules_list.extend(aws_services_discovery_rules)
        if len(aws_services_ecs_cluster_rules) > 0:
            logging.info("Generated aws-nuke filter for ECSCluster resource")
            specific_rules_list.extend(aws_services_ecs_cluster_rules)
        return specific_rules_list

    def _generate_aws_nuke_general_configuration_rules_environment(self, environment_name):
        logging.info(f"Generating aws-nuke filter for {', '.join(_aws_common_resources_list)} AWS resources")
        return [
            self._generate_rule_aws_nuke_equal_to_value("CloudWatchLogsLogGroup", environment_name),
            self._generate_rules_aws_nuke_contains("CloudWatchAlarm", environment_name),
            self._generate_rules_aws_nuke_has_property("CloudFormationStack", "tag:Environment", environment_name),
            self._generate_rules_aws_nuke_contains("ElasticacheCacheCluster", environment_name),
            self._generate_rules_aws_nuke_contains("ElasticacheSubnetGroup", environment_name),
            self._generate_rules_aws_nuke_contains("ECSService", environment_name),
            self._generate_rules_aws_nuke_contains("ECSTaskDefinition", environment_name),
            self._generate_rules_aws_nuke_has_property("ELBv2", "tag:Environment", environment_name),
            self._generate_rules_aws_nuke_has_property("ELBv2TargetGroup", "tag:Environment", environment_name),
            self._generate_rule_aws_nuke_property_contains("EC2SecurityGroup", "Name", environment_name),
        ]

    def _generate_aws_nuke_configuration_for_service_discovery_environment(self, environment_name):
        aws_nuke_rules_services = []
        aws_nuke_rules_service_discovery_namespace = self._generate_servicediscovery_namespace_rules(environment_name)
        if len(aws_nuke_rules_service_discovery_namespace) > 0:
            aws_nuke_rules_services.append(aws_nuke_rules_service_discovery_namespace)
            namespace_id = aws_nuke_rules_service_discovery_namespace["ServiceDiscoveryNamespace"][0]["value"]
            aws_nuke_rules_service_discovery_services = (
                self._generate_resources_rules_aws_services_of_namespace_in_environment(environment_name, namespace_id)
            )
            aws_nuke_rules_services.append(aws_nuke_rules_service_discovery_services)
        return aws_nuke_rules_services

    def _generate_servicediscovery_namespace_rules(self, environment_name):
        aws_nuke_entry_namespace = {}
        logging.info(
            "Checking if there is a namespace for service discovery of environment {}".format(environment_name)
        )
        servicediscovery_namespaces_list_call = subprocess.Popen(
            ["aws", "servicediscovery", "list-namespaces", "--region", "us-east-1"], stdout=subprocess.PIPE
        )
        actual_namespaces = json.loads(servicediscovery_namespaces_list_call.stdout.read())
        if self._check_servicediscovery_namespace_exists(actual_namespaces, environment_name):
            namespace_id = self._get_servicediscovery_id(actual_namespaces, environment_name)
            logging.info(
                "Exists namespace for service discovery of environment {} with id {}".format(
                    environment_name, namespace_id
                )
            )
            aws_nuke_entry_namespace.update(
                {"ServiceDiscoveryNamespace": self._create_dict_entry_aws_nuke_value_invert(namespace_id)}
            )
        else:
            logging.error("Doesn't exists namespace for servicediscovery of environment {}".format(environment_name))
        return aws_nuke_entry_namespace

    def _generate_ecs_cluster_for_environment_rules(self, environment_name):
        aws_nuke_entry_cluster = []
        logging.info("Checking if there is an ECS cluster for environment {}".format(environment_name))
        ecs_clusters_list_call = subprocess.Popen(
            ["aws", "ecs", "list-clusters", "--region", "us-east-1"], stdout=subprocess.PIPE
        )
        actual_ecs_clusters = json.loads(ecs_clusters_list_call.stdout.read())["clusterArns"]
        if len(actual_ecs_clusters) > 0:
            for element in actual_ecs_clusters:
                if environment_name in element:
                    logging.info("There is an ECS cluster for environment {}".format(environment_name))
                    aws_nuke_entry_cluster.append(self._generate_rule_aws_nuke_equal_to_value("ECSCluster", element))
                    break
        return aws_nuke_entry_cluster

    @staticmethod
    def _check_servicediscovery_namespace_exists(actual_namespaces, environment_name):
        environment_namespace_name = environment_name + ".local"
        if any(namespaces["Name"] == environment_namespace_name for namespaces in actual_namespaces["Namespaces"]):
            return True
        return False

    @staticmethod
    def _get_servicediscovery_id(actual_namespaces_json, environment_name):
        namespace_name = environment_name + ".local"
        for element in actual_namespaces_json["Namespaces"]:
            if element["Name"] == namespace_name:
                return element["Id"]

    @staticmethod
    def _get_services_in_namespace(environment_name, namespace_id):
        services = []
        logging.info("Recovering services associated with namespace {}".format(namespace_id))
        servicediscovery_services_list_call = subprocess.Popen(
            ["aws", "servicediscovery", "list-services", "--region", "us-east-1"], stdout=subprocess.PIPE
        )
        actual_services = json.loads(servicediscovery_services_list_call.stdout.read())
        for element in actual_services["Services"]:
            if environment_name in element["Name"]:
                services.append({"service_id": element["Id"]})
        return services

    def _generate_resources_rules_aws_services_of_namespace_in_environment(self, environment_name, namespace_id):
        aws_nuke_entry_services = {}
        services = self._get_services_in_namespace(environment_name, namespace_id)
        if len(services) > 0:
            services_aws_nuke_entry = self._create_dict_entry_aws_nuke_service_discovery_services(services)
            aws_nuke_entry_services.update({"ServiceDiscoveryService": services_aws_nuke_entry})
        return aws_nuke_entry_services

    def _generate_rules_aws_nuke_contains(self, resource_name, environment_name):
        return {resource_name: self._create_dict_entry_aws_nuke_contains(environment_name)}

    def _generate_rules_aws_nuke_has_property(self, resource_name, resource_property, environment_name):
        return {resource_name: self._create_dict_entry_aws_nuke_property(resource_property, environment_name)}

    def _generate_rule_aws_nuke_equal_to_value(self, resource_name, environment_name):
        return {resource_name: self._create_dict_entry_aws_nuke_value_invert(environment_name)}

    def _generate_rule_aws_nuke_regex_list_split_by_char(self, resource_name, l_arg, split_char):
        return {resource_name: self._create_dict_entry_aws_nuke_regex_list_split_by_char(l_arg, split_char)}

    def _generate_rule_aws_nuke_property_contains(self, resource_name, prop, value):
        return {resource_name: self._create_dict_entry_aws_nuke_property_contains(prop, value)}

    def _generate_rule_aws_nuke_regex(self, resource_name, v):
        return {resource_name: self._create_dict_entry_aws_nuke_regex(v)}

    @staticmethod
    def _create_dict_entry_aws_nuke_value_invert(value):
        return [{"value": value, "invert": True}]

    @staticmethod
    def _create_dict_entry_aws_nuke_regex_list_split_by_char(l_arg, split_char):
        return [{"type": "regex", "value": split_char.join(l_arg), "invert": True}]

    @staticmethod
    def _create_dict_entry_aws_nuke_property(prop, v):
        return [{"property": prop, "value": v, "invert": True}]

    @staticmethod
    def _create_dict_entry_aws_nuke_property_contains(prop, v):
        return [{"type": "contains", "property": prop, "value": v, "invert": True}]

    @staticmethod
    def _create_dict_entry_aws_nuke_contains(v):
        return [{"type": "contains", "value": v, "invert": True}]

    @staticmethod
    def _create_dict_entry_aws_nuke_regex(v):
        return [{"value": v, "type": "regex", "invert": True}]

    @staticmethod
    def _create_dict_entry_aws_nuke_service_discovery_services(services):
        dict_entry_list = ""
        for index in range(len(services)):
            for key in services[index]:
                if index == 0:
                    dict_entry_list = services[index]["service_id"]
                else:
                    dict_entry_list = dict_entry_list + "|" + services[index]["service_id"]
        return [{"type": "regex", "value": dict_entry_list, "invert": True}]

    @staticmethod
    def _add_aws_entries_rule_to_config(l_arg):
        with open(_config_template) as file:
            config_yaml_file = yaml.load(file, Loader=yaml.FullLoader)
        for element in l_arg:
            for k, v in element.items():
                config_yaml_file["accounts"]["374050862540"]["filters"][k] = v
        with open(_config_file, "w") as file:
            yaml.dump(config_yaml_file, file)


if __name__ == "__main__":
    argv = sys.argv[1:]

    try:
        opts, args = getopt.getopt(argv, "he:", ["environment="])
    except getopt.GetoptError:
        _print_usage()
        sys.exit(2)

    if argv[0] != "-h" and (argv[0] != "-e"):
        _print_usage()
        sys.exit(2)

    _, environment = opts.pop(0)

    service_discovery_instance = AWSNukeConfigurationGenerator()
    AWSNukeConfigurationGenerator().generate_config_aws_nuke(environment)

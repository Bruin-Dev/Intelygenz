#!/bin/python


import json
import logging
import os
import subprocess

logging.basicConfig(level=logging.INFO)

FNULL = open(os.devnull, "w")


class ApplicationLoadBalancer:
    @staticmethod
    def _check_alb_exists(environment):
        alb_exists = {"exists": False}
        alb_list_call = subprocess.Popen(
            ["aws", "elbv2", "describe-load-balancers", "--region", "us-east-1"], stdout=subprocess.PIPE, stderr=FNULL
        )
        alb_list = json.loads(alb_list_call.stdout.read())
        albs = alb_list["LoadBalancers"]
        if len(albs) > 0:
            for element in albs:
                if element["LoadBalancerName"] == environment and element["Type"] == "application":
                    alb_exists.update({"exists": True, "alb_information": element})
        return alb_exists

    @staticmethod
    def _get_targets_groups_for_alb_and_cluster(alb_arn, environment):
        target_groups = []
        target_group_list_call = subprocess.Popen(
            ["aws", "elbv2", "describe-target-groups", "--region", "us-east-1"], stdout=subprocess.PIPE, stderr=FNULL
        )
        target_group_list = json.loads(target_group_list_call.stdout.read())["TargetGroups"]
        if len(target_group_list) > 0:
            for element in target_group_list:
                if element["LoadBalancerArns"]:
                    for targetgroup_alb_arn in element["LoadBalancerArns"]:
                        if alb_arn == targetgroup_alb_arn:
                            target_groups.append(element)
                elif environment in element["TargetGroupName"]:
                    target_groups.append(element)
        return target_groups

    def _delete_targets_group_for_alb(self, alb_arn, environment):
        logging.info("Checking if there are target groups associated with {} ALB".format(environment))
        target_groups_to_delete = self._get_targets_groups_for_alb_and_cluster(alb_arn, environment)
        num_target_groups_to_delete = len(target_groups_to_delete)
        if num_target_groups_to_delete > 0:
            logging.info("The ALB {} has {} associated target groups".format(environment, num_target_groups_to_delete))
            for i in range(len(target_groups_to_delete)):
                target_group_arn = target_groups_to_delete[i]["TargetGroupArn"]
                target_group_name = target_groups_to_delete[i]["TargetGroupName"]
                logging.info(
                    "Deleting target group with name {} and arn {}".format(target_group_arn, target_group_name)
                )
                subprocess.call(
                    ["aws", "elbv2", "delete-target-group", "--target-group-arn", target_group_arn], stdout=FNULL
                )

    def delete_alb(self, environment):
        logging.info("Checking if there is an ALB related with the environment {}".format(environment))
        alb_exists = self._check_alb_exists(environment)
        if alb_exists["exists"]:
            logging.info("There is an ALB related with the environment {}".format(environment))
            alb_arn = alb_exists["alb_information"]["LoadBalancerArn"]
            logging.info("ALB cluster ARN is: {}".format(alb_arn))
            logging.info("Deleting alb with name {} and arn {}".format(environment, alb_arn))
            subprocess.call(["aws", "elbv2", "delete-load-balancer", "--load-balancer-arn", alb_arn], stdout=FNULL)
            self._delete_targets_group_for_alb(alb_arn, environment)
        else:
            logging.error("There isn't an ALB related with the environment {}".format(environment))

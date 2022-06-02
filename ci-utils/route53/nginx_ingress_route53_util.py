#!/usr/bin/env python3

import argparse
import json
import os

import boto3
from kubernetes import client, config
from tenacity import retry, stop_after_delay, wait_exponential

# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config(os.path.join(os.environ["HOME"], ".kube/config"))


class Route53Util:
    _v1 = client.CoreV1Api()
    _nginx_ingress_namespace = "kube-system"
    _nginx_ingress_labels = "app=nginx-ingress,component=controller"
    _elb_client = boto3.client("elb")
    _route53_client = boto3.client("route53")

    def _get_pod_name_nginx_ingress(self):
        print("Obtaining pod name for nginx ingress")
        ret = self._v1.list_namespaced_pod(
            namespace=self._nginx_ingress_namespace, label_selector=self._nginx_ingress_labels, watch=False
        )
        if ret.items:
            pod_name = ret.items[0].metadata.name
            print(f"The name of the pod is {pod_name}")
            return pod_name
        else:
            print(
                f"No pod found for nginx ingress in namespace {self._nginx_ingress_namespace} "
                f"with labels {self._nginx_ingress_labels}"
            )

    @retry(wait=wait_exponential(multiplier=5, min=5), stop=stop_after_delay(900))
    def _wait_pod_nginx_ingress_is_ready(self, pod_name_arg):
        nginx_ingress_pod_status = self._v1.list_namespaced_pod(
            namespace=self._nginx_ingress_namespace, field_selector="metadata.name=" + pod_name_arg, watch=False
        )
        if nginx_ingress_pod_status.items:
            conditions = nginx_ingress_pod_status.items[0].status.conditions
            actual_status = [elem for elem in conditions if elem.type == "ContainersReady"][0].status
            if actual_status:
                print(f"The pod {pod_name_arg} has ContainersReady status")
            else:
                print(f"The pod {pod_name_arg} hasn't ContainersReady status yet. Retrying")
                raise Exception
        else:
            print("There isn't a pod with the specified name")
            exit(1)

    @retry(wait=wait_exponential(multiplier=5, min=5), stop=stop_after_delay(900))
    def _get_load_balancer_hostname_nginx_ingress(self):
        ret = self._v1.list_namespaced_service(
            namespace=self._nginx_ingress_namespace, label_selector=self._nginx_ingress_labels
        )
        print("Obtaining hostname of nginx ingress ELB")
        if ret.items and ret.items[0].status.load_balancer.ingress:
            elb_ingress_hostname = ret.items[0].status.load_balancer.ingress[0].hostname
            print(f"The hostname of nginx ingress ELB is {elb_ingress_hostname}")
            return elb_ingress_hostname
        else:
            print(f"No load balancer ingress present yet")
            raise Exception

    @retry(wait=wait_exponential(multiplier=5, min=5), stop=stop_after_delay(900))
    def _get_elb_hosted_zone_id(self, elb_dns_name_arg):
        elbs = self._elb_client.describe_load_balancers()

        print(f"Obtaining CanonicalHostedZoneNameID for ELB with DNS Name {elb_dns_name_arg}")

        for elb in elbs["LoadBalancerDescriptions"]:
            if elb["DNSName"] == elb_dns_name_arg:
                canonical_hosted_zone_id = elb["CanonicalHostedZoneNameID"]
                print(
                    f"CanonicalHostedZoneNameID for ELB with DNS Name {elb_dns_name_arg} is {canonical_hosted_zone_id}"
                )
                return canonical_hosted_zone_id

        print("No CanonicalHostedZoneNameID found for ELB with DNS Name yet ")
        raise Exception

    def _get_hosted_zone_to_change_id(self):
        hosted_zone_name = parser.parse_args().hosted_zone_name
        print(f"Obtaining hosted zone id for hosted zone with name {hosted_zone_name}")
        hosted_zones = self._route53_client.list_hosted_zones()
        for hosted_zone in hosted_zones["HostedZones"]:
            if hosted_zone["Name"] == hosted_zone_name:
                hosted_zone_id = hosted_zone["Id"]
                print(f"Id for hosted zone with name {hosted_zone_name} is {hosted_zone_id}")
                return hosted_zone_id
        print(f"Id for hosted zone with name {hosted_zone_name} not found")
        exit(1)

    @staticmethod
    def _get_action_from_args(update, delete):
        if update:
            return "UPSERT"
        elif delete:
            return "DELETE"
        else:
            print("Invalidad action provided")
            exit(1)

    def _do_action_in_route53_record(
        self, elb_hosted_zone_id, hosted_zone_to_change_id, elb_dns_ingress_hostname, update, delete
    ):
        action = self._get_action_from_args(update, delete)
        record_alias_name = parser.parse_args().record_alias_name
        change_batch = {
            "Comment": "Update kre record set",
            "Changes": [
                {
                    "Action": action,
                    "ResourceRecordSet": {
                        "Name": record_alias_name,
                        "Type": "A",
                        "AliasTarget": {
                            "HostedZoneId": elb_hosted_zone_id,
                            "DNSName": elb_dns_ingress_hostname,
                            "EvaluateTargetHealth": True,
                        },
                    },
                },
            ],
        }
        print(
            f"It's going to do action {action} in the the "
            f"Hosted Zone with Id {hosted_zone_to_change_id} "
            f"with the following Change Batch: \n"
            f"{json.dumps(change_batch, default=str, indent=4)}"
        )
        response = self._route53_client.change_resource_record_sets(
            HostedZoneId=hosted_zone_to_change_id, ChangeBatch=change_batch
        )
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            change_id = response["ChangeInfo"]["Id"]
            print(f"Change with id {change_id} applyed successfully. It will wait until it has INSYNC status")
            return change_id
        else:
            print(f"Errors appliying change in route53")
            exit(1)

    @retry(wait=wait_exponential(multiplier=5, min=5), stop=stop_after_delay(900))
    def _wait_until_route53_change_is_propagated(self, change_id):
        print(f"Obtaining result of change in route53 with id {change_id}")
        change_result = self._route53_client.get_change(Id=change_id)
        if change_result["ChangeInfo"]["Status"] == "INSYNC":
            print(f"Change with id {change_id} has INSYNC state in Route53, update finished successfully")
        elif change_result["ChangeInfo"]["Status"] == "PENDING":
            print(f"Change with id {change_id} has PENDING state in Route53")
            raise Exception
        else:
            print(f"Error getting state for change with {change_id}")
            exit(1)

    def _do_necessary_actions(self, update, delete):
        pod_name = self._get_pod_name_nginx_ingress()
        self._wait_pod_nginx_ingress_is_ready(pod_name)
        elb_dns_ingress_hostname = self._get_load_balancer_hostname_nginx_ingress()
        elb_canonical_hosted_zone_id = self._get_elb_hosted_zone_id(elb_dns_ingress_hostname)
        hosted_zone_to_change_id = self._get_hosted_zone_to_change_id()
        change_id = self._do_action_in_route53_record(
            elb_canonical_hosted_zone_id, hosted_zone_to_change_id, elb_dns_ingress_hostname, update, delete
        )
        self._wait_until_route53_change_is_propagated(change_id)

    def check_conditions(self):
        update_action = parser.parse_args().update
        delete_action = parser.parse_args().delete
        if not update_action and not delete_action:
            print("It's necessary provide an action to do: " "-d/--delete True | -/--update True")
            exit(1)
        elif update_action and delete_action:
            print("It's only possible select True for one action: " "-d/--delete True | -u/--update True")
            exit(1)
        elif update_action:
            print("It's going to do an update action in the record set")
            self._do_necessary_actions(True, False)
        elif delete_action:
            print("It's going to do a delete action in the record set")
            self._do_necessary_actions(False, True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--record_alias_name", type=str, help="Record alias name", required=True)
    parser.add_argument("-n", "--hosted_zone_name", type=str, help="Hosted zone name", required=True)
    parser.add_argument(
        "-u",
        "--update",
        type=bool,
        help="Flag to indicate update action in the record set",
        required=False,
        default=False,
    )
    parser.add_argument(
        "-d",
        "--delete",
        type=bool,
        help="Flag to indicate delete action in the record set",
        required=False,
        default=False,
    )
    route53 = Route53Util()
    route53.check_conditions()

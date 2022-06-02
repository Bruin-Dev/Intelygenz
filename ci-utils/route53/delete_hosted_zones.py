#!/usr/bin/env python3

import argparse
import json
import os

import boto3
from tenacity import retry, stop_after_delay, wait_exponential


class Route53DeleteHostedZones:
    _route53_client = boto3.client("route53")

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

    def _get_all_records_to_delete_in_hosted_zone(self, hosted_zone_id):
        record_sets_to_delete = []

        record_sets_response = self._route53_client.list_resource_record_sets(
            HostedZoneId=hosted_zone_id,
        )

        resource_record_sets = record_sets_response.get("ResourceRecordSets")
        if resource_record_sets:
            for record_set in resource_record_sets:
                if record_set["Type"] not in ["SOA", "NS"]:
                    record_sets_to_delete.append(record_set)

        return record_sets_to_delete

    def _delete_records_in_route53_hosted_aone(self, record_sets_to_delete, hosted_zone_to_change_id):
        for record_set_to_delete in record_sets_to_delete:
            change_batch = {
                "Comment": "Delete kre record set",
                "Changes": [
                    {"Action": "DELETE", "ResourceRecordSet": record_set_to_delete},
                ],
            }
            print(
                f"It's going to delete in the the "
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
                self._wait_until_route53_change_is_propagated(change_id)
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

    def do_necessary_actions(self):
        hosted_zone_to_change_id = self._get_hosted_zone_to_change_id()
        records_to_delete = self._get_all_records_to_delete_in_hosted_zone(hosted_zone_to_change_id)
        if records_to_delete:
            self._delete_records_in_route53_hosted_aone(records_to_delete, hosted_zone_to_change_id)
        else:
            print(f"There is no record sets to delete in hosted zone with id {hosted_zone_to_change_id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--hosted_zone_name", type=str, help="Hosted zone name", required=True)
    route53 = Route53DeleteHostedZones()
    route53.do_necessary_actions()

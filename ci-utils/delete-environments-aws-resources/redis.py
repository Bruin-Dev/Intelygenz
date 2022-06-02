#!/bin/python


import json
import logging
import os
import subprocess
import time

import common_utils as common_utils_module

logging.basicConfig(level=logging.INFO)

FNULL = open(os.devnull, "w")


class RedisCluster:
    def delete_redis_resources(self, environment):
        redis_cluster_delete_result = self._delete_redis_cluster(environment)
        redis_cache_subnet_group_result = self._delete_cache_subnet_group(environment)
        result_delete_redis_resources = self._check_delete_redis_resources(
            redis_cluster_delete_result, redis_cache_subnet_group_result
        )
        return result_delete_redis_resources

    @staticmethod
    def _check_delete_redis_resources(redis_cluster_delete_result, redis_cache_subnet_group_result):
        redis_resources_delete_result = {}
        if (redis_cluster_delete_result["exists"] and redis_cluster_delete_result["success_delete"]) or (
            not redis_cluster_delete_result["exists"]
        ):
            redis_resources_delete_result_redis = True
        else:
            redis_resources_delete_result_redis = False
        if (redis_cache_subnet_group_result["exists"] and redis_cache_subnet_group_result["success_delete"]) or (
            not redis_cache_subnet_group_result["exists"]
        ):
            redis_resources_delete_subnet_group = True
        else:
            redis_resources_delete_subnet_group = False
        redis_resources_delete_result.update(
            {
                "redis_cluster": redis_resources_delete_result_redis,
                "redis_subnet_group": redis_resources_delete_subnet_group,
            }
        )
        return redis_resources_delete_result

    def _delete_redis_cluster(self, environment):
        redis_cluster = self._check_redis_cluster_exists(environment)
        logging.info(
            "Checking if there is a ElastiCache Redis Cluster related with the environment {}".format(environment)
        )
        cluster_delete_result = {}
        if redis_cluster["exists"]:
            logging.info(
                "There is a ElastiCache Redis cluster related with environment exists and has {} cache nodes".format(
                    environment, redis_cluster["redis_cluster_information"]["CacheClusters"][0]["NumCacheNodes"]
                )
            )
            logging.info("Redis cluster {} it's going to be deleted".format(environment))
            subprocess.call(
                [
                    "aws",
                    "elasticache",
                    "delete-cache-cluster",
                    "--cache-cluster-id",
                    environment,
                    "--region",
                    "us-east-1",
                ],
                stdout=FNULL,
            )
            start_time = time.time()
            exit_status_delete = self._check_redis_cluster_is_deleted(environment, start_time)
            cluster_delete_result.update({"exists": redis_cluster["exists"], "success_delete": exit_status_delete})
        else:
            logging.error("There isn't a ElastiCache Redis cluster related with the environment {}".format(environment))
            cluster_delete_result.update({"exists": redis_cluster["exists"]})
        return cluster_delete_result

    @staticmethod
    def _check_redis_cluster_exists(environment):
        redis_cluster_exists = {}
        try:
            redis_cluster_call = subprocess.Popen(
                [
                    "aws",
                    "elasticache",
                    "describe-cache-clusters",
                    "--cache-cluster-id",
                    environment,
                    "--region",
                    "us-east-1",
                ],
                stdout=subprocess.PIPE,
                stderr=FNULL,
            )
            redis_cluster = json.loads(redis_cluster_call.stdout.read())
            if redis_cluster is not None:
                redis_cluster_exists.update({"exists": True, "redis_cluster_information": redis_cluster})
        except ValueError as e:
            redis_cluster_exists.update({"exists": False})
        return redis_cluster_exists

    def _check_redis_cluster_is_deleted(self, environment, start_time):
        timeout = start_time + 60 * 5
        correct_exit = False
        actual_time = time.time()
        while timeout > actual_time:
            redis_cluster_status = self._check_redis_cluster_exists(environment)
            if redis_cluster_status["exists"]:
                logging.info("Waiting for Redis cluster {} to be deleted".format(environment))
                logging.info(
                    "Time elapsed for delete ElastiCache Redis cluster {} is  {} seconds".format(
                        environment, actual_time - start_time
                    )
                )
                logging.info(
                    "Actual state of ElastiCache Redis cluster is: {}".format(
                        redis_cluster_status["redis_cluster_information"]["CacheClusters"][0]["CacheClusterStatus"]
                    )
                )
                time.sleep(30)
                actual_time = time.time()
            else:
                logging.info("ElastiCache Redis cluster {} has been deleted successfully".format(environment))
                correct_exit = True
                break
        if timeout > actual_time and not correct_exit:
            logging.error(
                "The maximum waiting time for deleting the ElastiCache Redis cluster "
                "{} ({} seconds) has elapsed and it has not been possible to delete it".format(environment, timeout)
            )
        return correct_exit

    def _delete_cache_subnet_group(self, environment):
        logging.info("Checking if there is an ElastiCache Subnet Group for the environment {}".format(environment))
        cache_subnet_for_environment = self._check_redis_cache_subnet_group(environment)
        cache_subnet_for_environment_exists = cache_subnet_for_environment["exists"]
        cache_subnet_delete_result = {}
        if cache_subnet_for_environment_exists:
            common_utils_instance = common_utils_module.CommonUtils()
            cache_subnet_group_name = cache_subnet_for_environment["cache_subnet_information"]["CacheSubnetGroupName"]
            logging.info(
                "There is an ElastiCache Subnet Group for the environment {} with name".format(
                    environment, cache_subnet_group_name
                )
            )
            logging.info("ElastiCache Subnet Group {} it's going to be deleted".format(cache_subnet_group_name))
            cmd_call_remove_cache_subnet_group = (
                "aws, elasticache, delete-cache-subnet-group, " "--cache-subnet-group, " + cache_subnet_group_name
            )
            remove_cache_subnet_group = subprocess.call(cmd_call_remove_cache_subnet_group.split(", "), stdout=FNULL)
            common_utils_instance.check_current_state_call(
                remove_cache_subnet_group, "ElastiCache Subnet Group", cache_subnet_group_name
            )
            if remove_cache_subnet_group == 0:
                cache_subnet_delete_result.update(
                    {"exists": cache_subnet_for_environment_exists, "success_delete": True}
                )
            else:
                cache_subnet_delete_result.update(
                    {"exists": cache_subnet_for_environment_exists, "success_delete": False}
                )
        else:
            logging.error("There isn't a ElastiCache SubnetGroup for the environment {}".format(environment))
            cache_subnet_delete_result.update({"exists": cache_subnet_for_environment_exists})
        return cache_subnet_delete_result

    @staticmethod
    def _check_redis_cache_subnet_group(environment):
        redis_cache_subnet = {"exists": False}
        redis_subnet_group = environment + "-redis-subnet"
        redis_subnet_list_call = subprocess.Popen(
            [
                "aws",
                "elasticache",
                "describe-cache-subnet-groups",
                "--cache-subnet-group-name",
                redis_subnet_group,
                "--region",
                "us-east-1",
            ],
            stdout=subprocess.PIPE,
            stderr=FNULL,
        )
        try:
            redis_subnet_list = json.loads(redis_subnet_list_call.stdout.read())["CacheSubnetGroups"]
            if len(redis_subnet_list) > 0:
                redis_cache_subnet.update({"exists": True, "cache_subnet_information": redis_subnet_list[0]})
        except ValueError as e:
            pass
        return redis_cache_subnet
